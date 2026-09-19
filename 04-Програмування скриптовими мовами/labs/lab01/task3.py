"""
Завдання 3: Безпечне хешування, CSV-база та JSON-логування.

Варіант 7 (Алгоритм: sha384, мін довжина: 15).
"""

import csv
import functools
import hashlib
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


class ValidationError(Exception):
    """Власний виняток для помилок валідації введених даних."""

    pass


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
                record = create_user(username, password)
                writer.writerow(record)
            except (ValueError, ValidationError) as e:
                print(f"[-] Помилка реєстрації {username}: {e}")


def log_event(func):
    """Декоратор для запису спроб авторизації у JSON-файл."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        username = args[0] if args else kwargs.get("username", "unknown")
        result_status = "failure"

        try:
            result = func(*args, **kwargs)
            if result:
                result_status = "success"
            return result
        finally:
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, mode="r", encoding="utf-8") as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        pass

            logs.append(log_entry)
            with open(LOG_FILE, mode="w", encoding="utf-8") as f:
                json.dump(logs, f, indent=4, ensure_ascii=False)

    return wrapper


@log_event
def login(username: str, password: str) -> bool:
    """Автентифікація користувача за базою CSV."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми.")

    users_db = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                users_db.append((row[0], row[1]))

    for db_user, db_hash in users_db:
        if db_user == username:
            try:
                current_hash = generate_hash(password, PERSONAL_SALT)
                return current_hash == db_hash
            except ValidationError:
                # Введений пароль коротший за 15 символів, тому він точно
                # не відповідає хешу (хешувались тільки паролі >= 15)
                return False

    return False


COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_ORANGE = "\033[93m"
COLOR_RESET = "\033[0m"


def main() -> None:
    """Головна функція для виконання сценарію."""
    # 1. Дані для реєстрації (10 користувачів, паролі >= 15 символів)
    # Один з паролів навмисно зроблено коротким для перевірки ValidationError
    users_to_register = (
        ("admin", "SuperSecretAdmin123"),
        ("manager", "SecureManagerPass2026"),
        ("analyst", "ThreatIntelPassword!"),
        ("guest", "Short123"),  # Цей не пройде валідацію (< 15)
        ("developer", "DevEnvironmentKey!2026"),
        ("tester", "QualityAssurancePass"),
        ("operator", "SystemOperatorHash15"),
        ("ciso", "ChiefInfoSecurityOfficer"),
        ("auditor", "ComplianceAuditPass"),
        ("student", "LvivPolytechnicLab01"),
    )

    try:
        print("\n——— Реєстрація користувачів ———")
        create_users(users_to_register)
        print("[+] Базу користувачів успішно згенеровано.")

        # 2. Читання бази даних
        print("\n——— Вміст бази даних CSV ———")
        users_db = []
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            users_db = list(reader)

        print(f"{'Логін':<15} | {'Хеш пароля (sha384)'}")
        print("—" * 50)
        for user, pwd_hash in users_db:
            print(f"{user:<15} | {pwd_hash}")

        # 3. Тестування автентифікації
        print("\n——— Тестування авторизації ———")
        test_cases = [
            ("admin", "SuperSecretAdmin123"),  # Правильний
            ("admin", "WrongPassword2026!!"),  # Неправильний
            ("student", "LvivPolytechnicLab01"),  # Правильний
            ("hacker", "RandomMaliciousPass"),  # Неіснуючий користувач
            ("", ""),  # Порожні дані (викличе ValueError)
        ]

        for u, p in test_cases:
            try:
                is_auth = login(u, p)

                # Визначаємо статус і одразу додаємо потрібний колір
                if is_auth:
                    status = f"{COLOR_GREEN}ALLOW{COLOR_RESET}"
                else:
                    status = f"{COLOR_RED}DENY{COLOR_RESET}"

                print(f"Вхід для '{u}': {status}")

            except ValueError as e:
                # Оранжевий колір для помилок (наприклад, порожні логін/пароль)
                print(
                    f"{COLOR_ORANGE}Помилка входу для '{u}': {e}{COLOR_RESET}"
                )

        print("\n[+] Всі події залоговані у файл log.json.")

    # Оранжевий колір для системних помилок
    except FileNotFoundError:
        print(f"{COLOR_ORANGE}[-] Помилка: Файл не знайдено.{COLOR_RESET}")
    except PermissionError:
        print(
            f"{COLOR_ORANGE}[-] Помилка: Немає прав на запис/читання файлу.{
                COLOR_RESET
            }"
        )
    except IOError as e:
        print(f"{COLOR_ORANGE}[-] Помилка вводу/виводу: {e}{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_ORANGE}[-] Непередбачувана помилка: {e}{COLOR_RESET}")


if __name__ == "__main__":
    main()
