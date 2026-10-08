"""Завдання 2 (варіант 7): аналізатор журналів активності користувачів.

Утиліта читає CSV-журнал дій (Timestamp, UserID, Action, Resource, IP),
знаходить дії у позаробочий час (22:00-06:00 та вихідні) і користувачів
із масовими зверненнями до критичних ресурсів, логує тривоги та зберігає
підозрілі події у JSON-звіт.

Запуск: python -m labs.lab02.main analyze --activity-log ... (див. README).
"""

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED_COLUMNS = ("Timestamp", "UserID", "Action", "Resource", "IP")

# Позаробочий час: з 22:00 (включно) до 06:00 (не включно) та вихідні
OFF_HOURS_START = 22
OFF_HOURS_END = 6
WEEKEND_DAYS = (5, 6)  # субота, неділя
WEEKDAY_NAMES = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)

# Критичні ресурси та типові пороги масових звернень
DEFAULT_CRITICAL_PREFIXES = ("/prod", "/finance", "/admin")
DEFAULT_MASS_THRESHOLD = 10
DEFAULT_MASS_WINDOW_MIN = 60
DEFAULT_REPORT_NAME = "off_hours_audit.json"

# Власний рівень логування для тривог (між WARNING=30 та ERROR=40)
ALERT_LEVEL = 35
logging.addLevelName(ALERT_LEVEL, "ALERT")

logger = logging.getLogger("lab02.activity")


@dataclass(frozen=True)
class ActivityRecord:
    """Один рядок журналу активності."""

    timestamp: datetime
    user_id: str
    action: str
    resource: str
    ip: str

    def is_critical(self, prefixes: Sequence[str]) -> bool:
        """Перевіряє, чи ресурс лежить у каталозі зі списку критичних."""
        for prefix in prefixes:
            base = prefix.rstrip("/")
            if self.resource == base or self.resource.startswith(base + "/"):
                return True
        return False

    def to_dict(self) -> dict:
        """Повертає запис як словник, придатний для JSON."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat(sep=" ")
        return data


def positive_int(value: str) -> int:
    """Тип аргументу argparse: ціле число більше нуля."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{value}' не є цілим числом"
        ) from None
    if number <= 0:
        raise argparse.ArgumentTypeError("значення має бути більше нуля")
    return number


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Додає аргументи командного рядка команди analyze."""
    parser.add_argument(
        "--activity-log",
        type=Path,
        required=True,
        help="шлях до CSV-журналу активності користувачів",
    )
    parser.add_argument(
        "--after-hours",
        action="store_true",
        help="виявляти дії у позаробочий час (22:00-06:00 та вихідні)",
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=None,
        help=(
            "шлях до JSON-звіту (за замовчуванням "
            f"{DEFAULT_REPORT_NAME} поруч із журналом)"
        ),
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="файл для запису логів (тривоги та події обробки)",
    )
    parser.add_argument(
        "--critical-prefix",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "каталог критичних ресурсів (можна повторювати; за замовчуванням "
            + ", ".join(DEFAULT_CRITICAL_PREFIXES)
            + ")"
        ),
    )
    parser.add_argument(
        "--mass-threshold",
        type=positive_int,
        default=DEFAULT_MASS_THRESHOLD,
        help="мінімум звернень до критичних ресурсів для тривоги "
        f"(за замовчуванням {DEFAULT_MASS_THRESHOLD})",
    )
    parser.add_argument(
        "--mass-window-min",
        type=positive_int,
        default=DEFAULT_MASS_WINDOW_MIN,
        help="розмір ковзного вікна в хвилинах "
        f"(за замовчуванням {DEFAULT_MASS_WINDOW_MIN})",
    )


def configure_logging(log_file: Path | None) -> None:
    """Налаштовує логер: консоль (stdout) і, за потреби, файл."""
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console)

    if log_file is not None:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
        except OSError as error:
            logger.warning(
                "Не вдалося відкрити лог-файл %s: %s", log_file, error
            )
            return
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)


def read_activity(path: Path, errors: list[str]) -> Iterator[ActivityRecord]:
    """Генератор: читає CSV по одному рядку, некоректні рядки пропускає.

    Опис кожного пропущеного рядка додається до списку errors.
    """
    with path.open(mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = [
            c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])
        ]
        if missing:
            raise ValueError(f"у файлі відсутні колонки: {', '.join(missing)}")
        for row in reader:
            try:
                values = {
                    col: (row[col] or "").strip() for col in REQUIRED_COLUMNS
                }
                if not all(values.values()):
                    raise ValueError("порожнє значення")
                try:
                    timestamp = datetime.fromisoformat(values["Timestamp"])
                except ValueError:
                    raise ValueError(
                        f"некоректний формат часу {values['Timestamp']!r}"
                    ) from None
                if timestamp.tzinfo is not None:
                    raise ValueError("час має бути без часової зони")
                yield ActivityRecord(
                    timestamp=timestamp,
                    user_id=values["UserID"],
                    action=values["Action"],
                    resource=values["Resource"],
                    ip=values["IP"],
                )
            except (ValueError, AttributeError, TypeError) as error:
                errors.append(f"рядок {reader.line_num}: {error}")


def off_hours_reasons(timestamp: datetime) -> list[str]:
    """Повертає причини, чому час є позаробочим (порожній список - робочий)."""
    reasons = []
    if timestamp.weekday() in WEEKEND_DAYS:
        reasons.append("weekend")
    if timestamp.hour >= OFF_HOURS_START or timestamp.hour < OFF_HOURS_END:
        reasons.append("night")
    return reasons


def group_by_user(
    records: Sequence[ActivityRecord],
) -> defaultdict[str, list[ActivityRecord]]:
    """Групує дії за користувачами (collections.defaultdict)."""
    by_user: defaultdict[str, list[ActivityRecord]] = defaultdict(list)
    for record in records:
        by_user[record.user_id].append(record)
    return by_user


def find_off_hours(
    by_user: dict[str, list[ActivityRecord]],
    critical_prefixes: Sequence[str],
) -> list[dict]:
    """Знаходить дії у позаробочий час, відсортовані за часом."""
    events = []
    for user_id, user_records in by_user.items():
        for record in user_records:
            reasons = off_hours_reasons(record.timestamp)
            if not reasons:
                continue
            event = record.to_dict()
            event["weekday"] = WEEKDAY_NAMES[record.timestamp.weekday()]
            event["reasons"] = reasons
            event["critical_resource"] = record.is_critical(critical_prefixes)
            events.append(event)
    return sorted(events, key=lambda e: (e["timestamp"], e["user_id"]))


def find_mass_access(
    by_user: dict[str, list[ActivityRecord]],
    critical_prefixes: Sequence[str],
    threshold: int,
    window_min: int,
) -> list[dict]:
    """Знаходить користувачів, що за ковзне вікно мали >= threshold звернень.

    Враховуються лише звернення до критичних ресурсів. Для кожного
    користувача береться вікно з найбільшою кількістю звернень.
    """
    window = timedelta(minutes=window_min)
    alerts = []
    for user_id, user_records in by_user.items():
        critical = sorted(
            (r for r in user_records if r.is_critical(critical_prefixes)),
            key=lambda r: r.timestamp,
        )
        best_count, best_start, best_end = 0, 0, 0
        left = 0
        for right, record in enumerate(critical):
            while record.timestamp - critical[left].timestamp > window:
                left += 1
            if right - left + 1 > best_count:
                best_count, best_start, best_end = (
                    right - left + 1,
                    left,
                    right,
                )
        if best_count < threshold:
            continue
        in_window = critical[best_start : best_end + 1]
        started, finished = in_window[0].timestamp, in_window[-1].timestamp
        alerts.append(
            {
                "user_id": user_id,
                "count": best_count,
                "window_start": started.isoformat(sep=" "),
                "window_end": finished.isoformat(sep=" "),
                "duration_min": round(
                    (finished - started).total_seconds() / 60
                ),
                "resources": sorted({r.resource for r in in_window}),
                "ips": sorted({r.ip for r in in_window}),
            }
        )
    return sorted(alerts, key=lambda a: (-a["count"], a["user_id"]))


def format_off_hours_alert(event: dict) -> str:
    """Формує текст тривоги про дію у позаробочий час."""
    text = (
        f"Користувач '{event['user_id']}': {event['action']} "
        f"'{event['resource']}' о {event['timestamp']} "
        f"({event['weekday']}, {'+'.join(event['reasons'])}) "
        f"з IP {event['ip']}"
    )
    if event["critical_resource"]:
        text += " [критичний ресурс]"
    return text


def format_mass_alert(alert: dict) -> str:
    """Формує текст тривоги про масові звернення до критичних ресурсів."""
    return (
        f"Користувач '{alert['user_id']}': {alert['count']} звернень до "
        f"критичних ресурсів за {alert['duration_min']} хв "
        f"({alert['window_start']} - {alert['window_end']}) "
        f"з IP {', '.join(alert['ips'])}; ресурси: "
        f"{', '.join(alert['resources'])}"
    )


def save_report(report: dict, path: Path) -> None:
    """Зберігає звіт у JSON (UTF-8), створюючи відсутні каталоги."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)


def analyze(args: argparse.Namespace) -> int:
    """Виконує аналіз журналу. Повертає код завершення (0 - успіх)."""
    configure_logging(args.log_file)
    log_path: Path = args.activity_log
    report_path: Path = args.out_report or log_path.with_name(
        DEFAULT_REPORT_NAME
    )
    prefixes = tuple(args.critical_prefix or DEFAULT_CRITICAL_PREFIXES)

    logger.info("Читання журналу активності %s...", log_path)
    skipped: list[str] = []
    try:
        records = list(read_activity(log_path, skipped))
    except FileNotFoundError:
        logger.error("Файл журналу не знайдено: %s", log_path)
        return 1
    except PermissionError:
        logger.error("Немає прав на читання файлу: %s", log_path)
        return 1
    except (OSError, UnicodeDecodeError, csv.Error, ValueError) as error:
        logger.error("Не вдалося прочитати журнал %s: %s", log_path, error)
        return 1

    logger.info("Оброблено записів: %d.", len(records))
    for message in skipped:
        logger.warning("Пропущено некоректний %s", message)
    if skipped:
        logger.warning("Усього пропущено рядків: %d.", len(skipped))

    by_user = group_by_user(records)
    off_hours: list[dict] = []
    if args.after_hours:
        off_hours = find_off_hours(by_user, prefixes)
        print(
            "\n=== Активність у позаробочий час "
            f"({OFF_HOURS_START:02d}:00 - {OFF_HOURS_END:02d}:00 / "
            "вихідні) ==="
        )
        for event in off_hours:
            logger.log(ALERT_LEVEL, format_off_hours_alert(event))
        if not off_hours:
            print("Не виявлено.")

    mass = find_mass_access(
        by_user, prefixes, args.mass_threshold, args.mass_window_min
    )
    print(
        f"\n=== Масові звернення до критичних ресурсів "
        f"(>= {args.mass_threshold} за {args.mass_window_min} хв) ==="
    )
    for alert in mass:
        logger.log(ALERT_LEVEL, format_mass_alert(alert))
    if not mass:
        print("Не виявлено.")

    report = {
        "meta": {
            "source": str(log_path),
            "generated_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "records_processed": len(records),
            "rows_skipped": len(skipped),
            "users": len(by_user),
            "after_hours_check": args.after_hours,
            "critical_prefixes": list(prefixes),
            "mass_threshold": args.mass_threshold,
            "mass_window_min": args.mass_window_min,
        },
        "off_hours_events": off_hours,
        "mass_access_alerts": mass,
    }
    try:
        save_report(report, report_path)
    except OSError as error:
        logger.error("Не вдалося зберегти звіт %s: %s", report_path, error)
        return 1
    print()
    logger.info("Звіт про аномальну активність збережено: %s", report_path)
    return 0
