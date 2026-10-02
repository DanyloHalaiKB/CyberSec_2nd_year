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


def read_users_db() -> list:
    """Зчитує вміст CSV-файлу у список users_db."""
    users_db = []
    with open(CSV_FILE, mode="r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                users_db.append((row[0], row[1]))
    return users_db


def print_users_db(users_db: list) -> None:
    """Виводить базу користувачів у вигляді таблиці."""
    print(f"{'Логін':<15} | {'Хеш пароля (sha384)'}")
    print("—" * 50)
    for user, pwd_hash in users_db:
        print(f"{user:<15} | {pwd_hash}")


def print_login_result(username: str, is_auth: bool) -> None:
    """Виводить результат спроби входу."""
    # Визначаємо статус і одразу додаємо потрібний колір
    if is_auth:
        status = f"{COLOR_GREEN}ALLOW{COLOR_RESET}"
    else:
        status = f"{COLOR_RED}DENY{COLOR_RESET}"

    print(f"Вхід для '{username}': {status}")


def print_error(message: str) -> None:
    """Виводить повідомлення про помилку оранжевим кольором."""
    print(f"{COLOR_ORANGE}{message}{COLOR_RESET}")


def read_log() -> list:
    """Зчитує наявні події з файлу log.json."""
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="r", encoding="utf-8") as f:
            logs = json.load(f)
    return logs


def write_log(logs: list) -> None:
    """Записує список подій у файл log.json."""
    with open(LOG_FILE, mode="w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


def log_event(func):
    """Декоратор для запису спроб авторизації у JSON-файл.

    Тут зосереджено обробку всіх винятків спроби входу.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        username = args[0] if args else kwargs.get("username", "unknown")
        result_status = "failure"
        result = False

        try:
            result = func(*args, **kwargs)
            if result:
                result_status = "success"
            print_login_result(username, result)
        except ValidationError:
            # Введений пароль коротший за 15 символів, тому він точно
            # не відповідає хешу (хешувались тільки паролі >= 15)
            print_login_result(username, False)
        except ValueError as e:
            # Оранжевий колір для помилок (наприклад, порожні логін/пароль)
            print_error(f"Помилка входу '{username}': {e}")
        # Оранжевий колір для системних помилок
        except FileNotFoundError:
            print_error("[-] Помилка: Файл не знайдено.")
        except PermissionError:
            print_error("[-] Помилка: Немає прав на запис/читання файлу.")
        except IOError as e:
            print_error(f"[-] Помилка вводу/виводу: {e}")
        except Exception as e:
            print_error(f"[-] Непередбачувана помилка: {e}")
        finally:
            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            try:
                logs = read_log()
            except json.JSONDecodeError:
                logs = []

            logs.append(log_entry)
            write_log(logs)

        return result

    return wrapper


@log_event
def login(username: str, password: str) -> bool:
    """Автентифікація користувача за базою CSV."""
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми.")

    users_db = read_users_db()

    for db_user, db_hash in users_db:
        if db_user == username:
            current_hash = generate_hash(password, PERSONAL_SALT)
            return current_hash == db_hash

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

    print("\n——— Реєстрація користувачів ———")
    create_users(users_to_register)
    print("[+] Базу користувачів успішно згенеровано.")

    # 2. Читання бази даних
    print("\n——— Вміст бази даних CSV ———")
    users_db = read_users_db()
    print_users_db(users_db)

    # 3. Тестування автентифікації
    print("\n——— Тестування авторизації ———")
    test_cases = [
        ("admin", "SuperSecretAdmin123"),  # Правильний
        ("admin", "WrongPassword2026!!"),  # Неправильний
        ("student", "LvivPolytechnicLab01"),  # Правильний
        ("hacker", "RandomMaliciousPass"),  # Неіснуючий користувач
        ("", ""),  # Порожні дані (викличе ValueError)
    ]

    # Вивід результату та обробку винятків виконує декоратор @log_event
    for user, password in test_cases:
        login(user, password)

    print("\n[+] Всі події залоговані у файл log.json.")


if __name__ == "__main__":
    main()
