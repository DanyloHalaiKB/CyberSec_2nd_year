#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Talony MREO Bot — моніторинг вільних талонів на практичний іспит
(Е-запис ГСЦ МВС, https://eqn.hsc.gov.ua) зі сповіщеннями в Telegram.

Скрипт НІЧОГО не бронює. Він відкриває звичайне вікно Chromium, де ти один раз
входиш через ID.GOV.UA (Дія / BankID), і з цієї сторінки раз на кілька хвилин
читає ті самі JSON-дані, що й сам сайт. Коли з'являються нові вільні дати —
надсилає повідомлення в Telegram, а бронюєш ти сам.

Запуск:
    python monitor.py                 # основний режим
    python monitor.py --once          # одна перевірка, результат у консоль (без Telegram)
    python monitor.py --get-chat-id   # дізнатися свій chat_id (спершу напиши боту /start)
    python monitor.py --test-telegram # надіслати тестове повідомлення
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

BASE_URL = "https://eqn.hsc.gov.ua"
ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
STATE_PATH = ROOT / "state.json"
PROFILE_DIR = ROOT / "browser_profile"
LOG_PATH = ROOT / "monitor.log"

DEFAULTS: dict = {
    "telegram_token": "",
    "telegram_chat_id": "",
    # 49 = B, механічна КПП (авто сервісного центру)
    # 50 = B, автоматична КПП (авто сервісного центру)
    # 43 = B (авто навчального закладу / автошколи)
    "service_ids": [49],
    "region": "Львівська область",
    # Порожній список = всі ТСЦ регіону. Львівщина: 65 Львів (Апостола), 74 Львів (Богданівська),
    # 68 Самбір, 69 Стрий, 70 Шептицький
    "department_ids": [],
    "min_date": "",            # "YYYY-MM-DD" або "" — не раніше цієї дати
    "max_date": "",            # "YYYY-MM-DD" або "" — не пізніше цієї дати
    "interval_sec": 150,       # базовий інтервал між перевірками
    "jitter_sec": 40,          # випадкова добавка до інтервалу
    "pause_between_requests_sec": 8,  # пауза між запитами до API (сайт швидко віддає 429)
    "trust_allow_online_count": True,  # перевіряти дні лише там, де allowOnlineCount > 0
    "full_check_every_n_cycles": 10,   # раз на N циклів перевіряти всі ТСЦ (контроль)
    "reload_page_every_min": 20,
    "heartbeat_hours": 12,     # "я живий" раз на N годин; 0 = вимкнено
    "browser_channel": "",     # "" = вбудований Chromium Playwright; "chrome" = встановлений Google Chrome
    "prevent_sleep": True,     # Windows: не давати ПК заснути, поки скрипт працює
}

SERVICE_NAMES = {
    49: "категорія B, механічна КПП (авто СЦ)",
    50: "категорія B, автоматична КПП (авто СЦ)",
    43: "категорія B (авто автошколи)",
}
WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "нд"]

log = logging.getLogger("talony")


# ----------------------------------------------------------------------------- утиліти

def setup_logging() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    log.setLevel(logging.INFO)
    fh = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(ch)


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open(encoding="utf-8") as f:
            user = json.load(f)
        unknown = set(user) - set(DEFAULTS)
        if unknown:
            log.warning("Невідомі ключі в config.json (ігнорую): %s", ", ".join(sorted(unknown)))
        cfg.update({k: v for k, v in user.items() if k in DEFAULTS})
    else:
        log.warning("config.json не знайдено — використовую значення за замовчуванням")
    cfg["service_ids"] = [int(x) for x in cfg["service_ids"]]
    cfg["department_ids"] = [int(x) for x in cfg["department_ids"]]
    cfg["telegram_chat_id"] = str(cfg["telegram_chat_id"]).strip()
    cfg["telegram_token"] = str(cfg["telegram_token"]).strip()
    for key in ("min_date", "max_date"):
        if cfg[key]:
            date.fromisoformat(cfg[key])  # впаде з ValueError, якщо формат неправильний
    return cfg


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            with STATE_PATH.open(encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            log.warning("state.json пошкоджений — починаю з нуля")
    return {"seen": {}}


def save_state(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp.replace(STATE_PATH)


def fmt_day(iso: str) -> str:
    d = date.fromisoformat(iso[:10])
    return f"{d:%d.%m} ({WEEKDAYS[d.weekday()]})"


def prevent_windows_sleep(enable: bool) -> None:
    """Просить Windows не засинати, поки процес живий (без зміни налаштувань системи)."""
    if not enable or sys.platform != "win32":
        return
    try:
        import ctypes
        ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        log.info("Режим сну Windows заблоковано на час роботи скрипта")
    except Exception as e:  # не критично
        log.warning("Не вдалося заблокувати сон: %s", e)


# ----------------------------------------------------------------------------- Telegram

class Telegram:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        if not self.enabled:
            log.warning("Telegram не налаштований — повідомлення лише в лог:\n%s", text)
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML",
                   "disable_web_page_preview": True}
        for attempt in range(1, 4):
            try:
                r = requests.post(url, json=payload, timeout=20)
                if r.ok:
                    return True
                if r.status_code == 429:
                    wait = r.json().get("parameters", {}).get("retry_after", 5)
                    time.sleep(float(wait))
                    continue
                log.error("Telegram HTTP %s: %s", r.status_code, r.text[:300])
                if r.status_code in (400, 401, 403, 404):
                    return False  # неправильний токен/chat_id — повтор не допоможе
            except requests.RequestException as e:
                log.warning("Telegram недоступний (спроба %d): %s", attempt, e)
            time.sleep(3 * attempt)
        return False


def get_chat_id(token: str) -> None:
    if not token:
        print("Спершу встав telegram_token у config.json")
        return
    r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    data = r.json()
    if not data.get("ok"):
        print("Помилка Telegram:", data)
        return
    chats = {}
    for upd in data.get("result", []):
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat")
        if chat:
            chats[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name")
    if not chats:
        print("Повідомлень немає. Напиши своєму боту /start у Telegram і запусти ще раз.")
        return
    for cid, name in chats.items():
        print(f"chat_id = {cid}   ({name})")
    print("Встав потрібний chat_id у config.json → telegram_chat_id")


# ----------------------------------------------------------------------------- API Е-запису

class SessionExpired(Exception):
    pass


class RateLimited(Exception):
    pass


class ApiError(Exception):
    pass


# fetch виконується всередині сторінки eqn.hsc.gov.ua — з тими самими cookie, що й у сайту
FETCH_JS = """async (path) => {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 20000);
  try {
    const r = await fetch(path, {credentials: 'include', signal: ctrl.signal,
                                 headers: {'Accept': 'application/json, text/plain, */*'}});
    return {status: r.status, text: await r.text()};
  } catch (e) {
    return {status: -1, text: String(e)};
  } finally {
    clearTimeout(timer);
  }
}"""


class EqueueApi:
    def __init__(self, page, pause_sec: float):
        self.page = page
        self.pause = pause_sec
        self._last = 0.0

    def on_site(self) -> bool:
        return self.page.url.startswith(BASE_URL)

    def _raw(self, path: str) -> tuple[int, str]:
        if not self.on_site():
            raise SessionExpired(f"сторінка не на {BASE_URL}: {self.page.url[:80]}")
        wait = self.pause - (time.monotonic() - self._last)
        if wait > 0:
            self.page.wait_for_timeout(wait * 1000)
        res = self.page.evaluate(FETCH_JS, path)
        self._last = time.monotonic()
        return int(res["status"]), res["text"]

    def is_logged_in(self) -> bool:
        if not self.on_site():
            return False
        status, text = self._raw("/api/v2/oauth/session")
        if status != 200:
            return False
        try:
            data = json.loads(text)
        except ValueError:
            return False
        return isinstance(data, dict) and bool(data.get("account"))

    def get(self, path: str):
        status, text = self._raw(path)
        if status == 429:
            raise RateLimited(path)
        if status == 204:
            return None
        if status in (401, 403):
            # 401/403 — або закінчилась сесія, або захист сайту відхилив запит
            if not self.is_logged_in():
                raise SessionExpired(f"HTTP {status} на {path}")
            raise ApiError(f"HTTP {status} на {path} (сесія жива — можливо, блокування)")
        if status != 200:
            raise ApiError(f"HTTP {status} на {path}: {text[:200]}")
        try:
            return json.loads(text)
        except ValueError:
            raise SessionExpired(f"не JSON на {path} (ймовірно, редирект на вхід)")

    # --- конкретні запити (ті самі, що робить фронтенд сайту)
    def departments(self, service_id: int) -> list[dict]:
        data = self.get(f"/api/v2/equeue/departments?serviceId={service_id}")
        return (data or {}).get("data") or []

    def days(self, service_id: int, dept_id: int) -> list[str]:
        data = self.get(f"/api/v2/equeue/days?serviceId={service_id}&departmentId={dept_id}")
        return sorted(d["date"] for d in ((data or {}).get("data") or []) if d.get("date"))

    def slots(self, service_id: int, dept_id: int, day_iso: str) -> list[str]:
        data = self.get(f"/api/v2/equeue/slots?serviceId={service_id}"
                        f"&departmentId={dept_id}&date={day_iso}")
        return [s["startTime"][:5] for s in ((data or {}).get("data") or []) if s.get("startTime")]


# ----------------------------------------------------------------------------- логіка пошуку

@dataclass
class Found:
    service_id: int
    dept: dict
    days: list[str]                      # ISO "2026-10-16T00:00:00"
    first_day_slots: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.service_id}:{self.dept['id']}"


def dept_title(d: dict) -> str:
    addr = ", ".join(x.strip() for x in (d.get("city"), d.get("street"), d.get("building")) if x and x.strip())
    return f"{d.get('name', '').strip()} — {addr}"


def in_range(day_iso: str, cfg: dict) -> bool:
    d = day_iso[:10]
    if cfg["min_date"] and d < cfg["min_date"]:
        return False
    if cfg["max_date"] and d > cfg["max_date"]:
        return False
    return True


def scan(api: EqueueApi, cfg: dict, full_check: bool) -> list[Found]:
    results: list[Found] = []
    for sid in cfg["service_ids"]:
        deps = [d for d in api.departments(sid) if d.get("region") == cfg["region"]]
        if cfg["department_ids"]:
            deps = [d for d in deps if d.get("id") in cfg["department_ids"]]
        if not deps:
            log.warning("Послуга %s: у регіоні «%s» не знайдено жодного ТСЦ", sid, cfg["region"])
        for d in deps:
            count = d.get("allowOnlineCount") or 0
            if cfg["trust_allow_online_count"] and count <= 0 and not full_check:
                continue
            days = [x for x in api.days(sid, d["id"]) if in_range(x, cfg)]
            if days and count <= 0 and cfg["trust_allow_online_count"]:
                log.warning("Контроль: у %s є дні при allowOnlineCount=0 → далі перевіряю всі ТСЦ",
                            d.get("name"))
                cfg["trust_allow_online_count"] = False
            if not days:
                continue
            slots = api.slots(sid, d["id"], days[0])
            results.append(Found(sid, d, days, slots))
    return results


def build_message(f: Found, new_days: set[str]) -> str:
    service = SERVICE_NAMES.get(f.service_id, f"послуга {f.service_id}")
    day_parts = []
    for d in f.days[:12]:
        mark = " 🆕" if d in new_days else ""
        day_parts.append(f"{fmt_day(d)}{mark}")
    more = f" … і ще {len(f.days) - 12}" if len(f.days) > 12 else ""
    lines = [
        "🟢 <b>Вільні талони — практичний іспит</b>",
        f"<b>{html.escape(dept_title(f.dept))}</b>",
        f"Послуга: {html.escape(service)}",
        f"Дати: {', '.join(day_parts)}{more}",
    ]
    if f.first_day_slots:
        shown = ", ".join(f.first_day_slots[:10])
        extra = f" … (+{len(f.first_day_slots) - 10})" if len(f.first_day_slots) > 10 else ""
        lines.append(f"Час на {fmt_day(f.days[0])}: {shown}{extra}")
    lines.append(f"👉 {BASE_URL}/")
    return "\n".join(lines)


def process_results(found: list[Found], state: dict, tg: Telegram) -> int:
    """Надсилає повідомлення лише про НОВІ дати. Повертає кількість надісланих повідомлень."""
    seen: dict = state.setdefault("seen", {})
    current_keys = set()
    sent = 0
    for f in found:
        current_keys.add(f.key)
        prev = set(seen.get(f.key, []))
        new_days = set(f.days) - prev
        if new_days:
            msg = build_message(f, new_days)
            log.info("НОВІ ТАЛОНИ: %s — %s", f.dept.get("name"), ", ".join(sorted(x[:10] for x in new_days)))
            if tg.send(msg):
                sent += 1
        seen[f.key] = list(f.days)  # поточний стан: зникли й з'явились знову → повідомимо ще раз
    for k in list(seen):
        if k not in current_keys:
            del seen[k]
    return sent


# ----------------------------------------------------------------------------- браузер і цикл

def wait_for_login(page, api: EqueueApi, tg: Telegram) -> None:
    """Чекає, поки користувач сам увійде через ID.GOV.UA у відкритому вікні."""
    try:
        if api.on_site() and api.is_logged_in():
            return
    except Exception as e:
        log.debug("перевірка входу: %s", e)
    log.info("Потрібен вхід: у вікні браузера натисни «Увійти за допомогою ID.GOV.UA» і увійди.")
    tg.send("🔑 Потрібен вхід в Е-запис: відкрий вікно браузера скрипта на ПК і увійди через ID.GOV.UA.")
    if not page.url.startswith(("https://eqn.hsc.gov.ua", "https://id.gov.ua")):
        page.goto(BASE_URL + "/", wait_until="domcontentloaded")
    last_reminder = time.monotonic()
    while True:
        page.wait_for_timeout(10_000)
        try:
            if api.on_site() and api.is_logged_in():
                log.info("Вхід виконано")
                return
        except Exception as e:  # сторінка могла перезавантажитись посеред запиту
            log.debug("перевірка входу: %s", e)
        if time.monotonic() - last_reminder > 6 * 3600:
            tg.send("🔑 Досі чекаю на вхід в Е-запис (вікно браузера скрипта на ПК).")
            last_reminder = time.monotonic()


def open_browser(p, cfg: dict):
    kwargs = dict(
        user_data_dir=str(PROFILE_DIR),
        headless=False,
        locale="uk-UA",
        timezone_id="Europe/Kyiv",
        viewport={"width": 1200, "height": 850},
    )
    if cfg["browser_channel"]:
        kwargs["channel"] = cfg["browser_channel"]
    ctx = p.chromium.launch_persistent_context(**kwargs)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    return ctx, page


def run(cfg: dict, once: bool = False) -> None:
    from playwright.sync_api import Error as PWError
    from playwright.sync_api import sync_playwright

    tg = Telegram(cfg["telegram_token"], cfg["telegram_chat_id"]) if not once else Telegram("", "")
    state = load_state()
    prevent_windows_sleep(cfg["prevent_sleep"] and not once)

    with sync_playwright() as p:
        ctx, page = open_browser(p, cfg)
        api = EqueueApi(page, cfg["pause_between_requests_sec"])
        try:
            page.goto(BASE_URL + "/cabinet", wait_until="domcontentloaded")
            page.wait_for_timeout(4000)
            wait_for_login(page, api, tg)

            if once:
                found = scan(api, cfg, full_check=True)
                if not found:
                    print("Вільних талонів за заданими умовами немає.")
                for f in found:
                    print(build_message(f, set(f.days)).replace("<b>", "").replace("</b>", ""))
                    print()
                return

            services = ", ".join(SERVICE_NAMES.get(s, str(s)) for s in cfg["service_ids"])
            tg.send(f"✅ Моніторинг запущено\nРегіон: {html.escape(cfg['region'])}\n"
                    f"Послуги: {html.escape(services)}\nІнтервал: ~{cfg['interval_sec']} с")

            cycle = errors = 0
            backoff = 1
            last_reload = last_heartbeat = time.monotonic()
            total_checks = 0
            while True:
                cycle += 1
                try:
                    if "/queue" in page.url:
                        # користувач сам бронює в цьому вікні — не заважаємо
                        log.info("Відкрито сторінку запису — пауза моніторингу на 60 с")
                        page.wait_for_timeout(60_000)
                        continue
                    if time.monotonic() - last_reload > cfg["reload_page_every_min"] * 60:
                        page.goto(BASE_URL + "/cabinet", wait_until="domcontentloaded")
                        page.wait_for_timeout(4000)
                        last_reload = time.monotonic()
                    n = cfg["full_check_every_n_cycles"]
                    full = bool(n) and cycle % n == 0
                    found = scan(api, cfg, full_check=full)
                    sent = process_results(found, state, tg)
                    save_state(state)
                    total_checks += 1
                    log.info("Перевірка #%d%s: ТСЦ з талонами — %d, нових повідомлень — %d",
                             cycle, " (повна)" if full else "", len(found), sent)
                    errors, backoff = 0, 1
                except RateLimited as e:
                    backoff = min(backoff * 2, 8)
                    log.warning("429 Too many requests (%s) → збільшую інтервал ×%d", e, backoff)
                except SessionExpired as e:
                    log.warning("Сесія завершилась: %s", e)
                    tg.send("⚠️ Сесія Е-запису завершилась. Увійди знову у вікні браузера скрипта на ПК.")
                    page.goto(BASE_URL + "/", wait_until="domcontentloaded")
                    wait_for_login(page, api, tg)
                    tg.send("✅ Вхід виконано, моніторинг продовжується.")
                    page.goto(BASE_URL + "/cabinet", wait_until="domcontentloaded")
                    last_reload = time.monotonic()
                    continue
                except (ApiError, PWError) as e:
                    errors += 1
                    backoff = min(backoff * 2, 8)
                    log.error("Помилка (%d поспіль): %s", errors, e)
                    if errors == 5:
                        tg.send(f"❗ 5 помилок поспіль, моніторинг триває з паузами.\n"
                                f"Остання: {html.escape(str(e))[:300]}")
                    if errors % 3 == 0:
                        try:
                            page.goto(BASE_URL + "/cabinet", wait_until="domcontentloaded")
                            last_reload = time.monotonic()
                        except PWError:
                            pass

                hb = cfg["heartbeat_hours"]
                if hb and time.monotonic() - last_heartbeat > hb * 3600:
                    tg.send(f"ℹ️ Працюю. Успішних перевірок: {total_checks}. "
                            f"Зараз ТСЦ з талонами: {len(state.get('seen', {}))}.")
                    last_heartbeat = time.monotonic()

                delay = cfg["interval_sec"] * backoff + random.uniform(0, cfg["jitter_sec"])
                page.wait_for_timeout(delay * 1000)
        except KeyboardInterrupt:
            log.info("Зупинено користувачем (Ctrl+C)")
        finally:
            try:
                ctx.close()
            except Exception:
                pass


def main() -> None:
    setup_logging()
    ap = argparse.ArgumentParser(description="Моніторинг талонів на практичний іспит (Е-запис ГСЦ МВС)")
    ap.add_argument("--once", action="store_true", help="одна перевірка всіх ТСЦ, вивід у консоль")
    ap.add_argument("--get-chat-id", action="store_true", help="показати chat_id з повідомлень боту")
    ap.add_argument("--test-telegram", action="store_true", help="надіслати тестове повідомлення")
    args = ap.parse_args()

    cfg = load_config()
    if args.get_chat_id:
        get_chat_id(cfg["telegram_token"])
        return
    if args.test_telegram:
        ok = Telegram(cfg["telegram_token"], cfg["telegram_chat_id"]).send("👋 Тест: бот талонів підключений.")
        print("Надіслано" if ok else "Не вдалося — дивись monitor.log")
        return
    if not args.once and not (cfg["telegram_token"] and cfg["telegram_chat_id"]):
        log.error("Заповни telegram_token і telegram_chat_id у config.json (див. README.md)")
        sys.exit(1)
    run(cfg, once=args.once)


if __name__ == "__main__":
    main()
