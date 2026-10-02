"""
Завдання 3: Безпечне хешування, CSV-база та JSON-логування.

Варіант 7 (Алгоритм: sha384, мін довжина: 15).
"""

import csv
import functools
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime

# Додавання шляху до суміжної папки для імпорту модуля student.py
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from shared.student import VARIANT_NUMBER

# Константи для Варіанту 7
MIN_PASS_LENGTH = 15
PERSONAL_SALT = str(VARIANT_NUMBER).zfill(5)  # Згенерує "00007"

# Директорії та файли
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_DIR, "users.csv")
LOG_FILE = os.path.join(DATA_DIR, "log.json")

# ANSI-кольори для виводу в терміналі
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_ORANGE = "\033[93m"
COLOR_RESET = "\033[0m"


class ValidationError(Exception):
    """Власний виняток для помилок валідації введених даних."""


def generate_hash(password: str, salt: str = "00000") -> str:
    """Генерує хеш sha384 від конкатенації пароля та солі."""
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми.")

    if len(password) < MIN_PASS_LENGTH:
        raise ValidationError(
            f"Пароль надто короткий. Мінімум {MIN_PASS_LENGTH} символів."
        )

    combined = (password + salt).encode("utf-8")
    return hashlib.sha384(combined).hexdigest()


def create_user(username: str, password: str) -> tuple:
    """Хешує пароль з персональною сіллю та повертає запис."""
    hash_value = generate_hash(password, PERSONAL_SALT)
    return username, hash_value


def create_users(users_list: tuple) -> None:
    """Створює папку data та записує користувачів у CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for username, password in users_list:
            try:
                writer.writerow(create_user(username, password))
            except (ValueError, ValidationError) as e:
                print(f"[-] Помилка реєстрації {username}: {e}")


# Список users_db заповнює декоратор @log_event, зчитуючи CSV-файл
users_db: list[tuple[str, str]] = []


def log_event(func):
    """Декоратор спроби входу: зчитування даних, вивід і логування.

    Перед викликом функції зчитує CSV-базу у список users_db
    (при першому виклику ще й виводить її таблицею), після виклику
    виводить результат ALLOW/DENY або помилку, а у блоці finally
    зчитує log.json, дописує подію та зберігає журнал.
    Пароль у журнал не потрапляє.
    """
    db_shown = False  # чи виводилась уже таблиця бази

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal db_shown
        username = args[0] if args else kwargs.get("username", "unknown")
        result = False
        result_status = "failure"

        try:
            # 1. Зчитування CSV-бази у список users_db
            with open(CSV_FILE, mode="r", encoding="utf-8") as file:
                users_db[:] = [
                    (row[0], row[1])
                    for row in csv.reader(file)
                    if len(row) == 2  # пропускаємо порожні рядки
                ]

            # 2. Вивід бази таблицею (лише при першій спробі входу)
            if not db_shown:
                print("\n——— Вміст бази даних CSV ———")
                print(f"{'Логін':<15} | {'Хеш пароля (sha384)'}")
                print("—" * 50)
                for user, pwd_hash in users_db:
                    print(f"{user:<15} | {pwd_hash}")
                print("\n——— Тестування авторизації ———")
                db_shown = True

            # 3. Спроба входу та вивід результату
            result = func(*args, **kwargs)
            if result:
                result_status = "success"
                status = f"{COLOR_GREEN}ALLOW{COLOR_RESET}"
            else:
                status = f"{COLOR_RED}DENY{COLOR_RESET}"
            print(f"Вхід для '{username}': {status}")

        except (ValueError, ValidationError) as e:
            print(
                f"{COLOR_ORANGE}Помилка входу '{username}': {e}{COLOR_RESET}"
            )

        finally:
            # 4. Логування: пароль (другий аргумент) маскуємо
            safe_args = [args[0], "***"] if len(args) > 1 else list(args)
            safe_kwargs = {
                key: ("***" if key == "password" else value)
                for key, value in kwargs.items()
            }
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": safe_args,
                "kwargs": safe_kwargs,
            }
            try:
                # Зчитування наявного журналу
                logs = []
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, mode="r", encoding="utf-8") as f:
                        try:
                            logs = json.load(f)
                        except json.JSONDecodeError:
                            logs = []  # пошкоджений журнал — заново

                # Запис оновленого журналу
                logs.append(log_entry)
                with open(LOG_FILE, mode="w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=4, ensure_ascii=False)
            except OSError as e:
                # Помилка журналу не повинна перекрити результат входу
                print(f"{COLOR_ORANGE}[-] Лог не записано: {e}{COLOR_RESET}")

        return result

    return wrapper


@log_event
def login(username: str, password: str) -> bool:
    """Автентифікація користувача за базою users_db."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми.")

    for db_user, db_hash in users_db:
        if db_user == username:
            try:
                current_hash = generate_hash(password, PERSONAL_SALT)
            except ValidationError:
                # Пароль коротший за 15 символів не може збігтися з хешем
                return False
            # Порівняння за сталий час — захист від timing-атак
            return hmac.compare_digest(current_hash, db_hash)

    return False


def main() -> None:
    """Головна функція для виконання сценарію."""
    # Дані для реєстрації (10 користувачів, паролі >= 15 символів).
    # Один з паролів навмисно короткий для перевірки ValidationError.
    users_to_register = (
        ("admin", "SuperSecretAdmin123"),
        ("manager", "SecureManagerPass2026"),
        ("analyst", "ThreatIntelPassword!"),
        ("guest", "Short123"),  # Не пройде валідацію (< 15)
        ("developer", "DevEnvironmentKey!2026"),
        ("tester", "QualityAssurancePass"),
        ("operator", "SystemOperatorHash15"),
        ("ciso", "ChiefInfoSecurityOfficer"),
        ("auditor", "ComplianceAuditPass"),
        ("student", "LvivPolytechnicLab01"),
    )

    test_cases = [
        ("admin", "SuperSecretAdmin123"),  # Правильний
        ("admin", "WrongPassword2026!!"),  # Неправильний
        ("student", "LvivPolytechnicLab01"),  # Правильний
        ("hacker", "RandomMaliciousPass"),  # Неіснуючий користувач
        ("", ""),  # Порожні дані (ValueError)
    ]

    try:
        print("\n——— Реєстрація користувачів ———")
        create_users(users_to_register)
        print("[+] Базу користувачів успішно згенеровано.")

        # Зчитування бази, вивід і логування виконує декоратор @log_event
        for user, password in test_cases:
            login(user, password)

        print("\n[+] Всі події залоговані у файл log.json.")

    except FileNotFoundError as e:
        print(f"{COLOR_ORANGE}[-] Файл не знайдено: {e}{COLOR_RESET}")
    except PermissionError as e:
        print(f"{COLOR_ORANGE}[-] Немає прав доступу: {e}{COLOR_RESET}")
    except IOError as e:
        print(f"{COLOR_ORANGE}[-] Помилка вводу/виводу: {e}{COLOR_RESET}")


if __name__ == "__main__":
    main()
