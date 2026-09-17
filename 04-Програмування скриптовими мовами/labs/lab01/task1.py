"""Завдання 1: комплексний аналізатор надійності паролів.

Оцінює стійкість паролів до компрометації за критеріями
індивідуального варіанта та виводить результат таблицею.
"""

import os
import random
import string
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from shared.student import (  # noqa: E402
    GROUP_NAME,
    STUDENT_NAME,
    VARIANT_NUMBER,
)

PASSWORDS = [
    "NetworkS3c!",
    "easy",
    "Firewa11@Pass",
    "anonymous",
    "Intrus10n#Detect",
    "sample",
    "Malwar3@Scan",
    "qwerty",
    "Vulnerab1l!ty",
    "common",
]

CRITERIA = {
    "min_length": 9,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

FORBIDDEN_PASSWORDS = {
    "easy",
    "anonymous",
    "sample",
    "qwerty",
    "common",
    "password",
}

DUPLICATES_COUNT = 3
VERY_STRONG_BONUS = 4
MIDDLE_GROUPS = 2


def has_digit(password: str) -> bool:
    """Перевірити наявність хоча б однієї цифри."""
    return any(char.isdigit() for char in password)


def has_upper(password: str) -> bool:
    """Перевірити наявність хоча б однієї великої літери."""
    return any(char.isupper() for char in password)


def has_lower(password: str) -> bool:
    """Перевірити наявність хоча б однієї малої літери."""
    return any(char.islower() for char in password)


def has_special(password: str) -> bool:
    """Перевірити наявність хоча б одного спеціального символу."""
    return any(char in string.punctuation for char in password)


def count_char_groups(password: str) -> int:
    """Порахувати кількість різних груп символів у паролі.

    Групи: цифри, великі літери, малі літери, спецсимволи.
    Тип bool є підкласом int, тому True додається як одиниця.
    """
    return sum(
        [
            has_digit(password),
            has_upper(password),
            has_lower(password),
            has_special(password),
        ]
    )


def meets_all_criteria(password: str) -> bool:
    """Перевірити відповідність усім увімкненим вимогам політики."""
    if len(password) < CRITERIA["min_length"]:
        return False
    if CRITERIA["require_digits"] and not has_digit(password):
        return False
    if CRITERIA["require_upper"] and not has_upper(password):
        return False
    if CRITERIA["require_special"] and not has_special(password):
        return False
    return True


def is_forbidden(password: str) -> bool:
    """Перевірити, чи пароль заборонений політикою безпеки."""
    return (
        password in FORBIDDEN_PASSWORDS
        or len(password) < CRITERIA["min_length"]
    )


def is_unique(password: str, passwords: list[str]) -> bool:
    """Перевірити, чи пароль трапляється у списку рівно один раз."""
    return passwords.count(password) == 1


def add_duplicates(passwords: list[str], count: int) -> list[str]:
    """Повернути новий список із копіями випадкових паролів у кінці.

    Імітує повторне використання паролів. Вхідний список не
    змінюється: копія створюється методом copy().
    """
    extended = passwords.copy()
    for _ in range(count):
        index = random.randint(0, len(passwords) - 1)
        extended.append(passwords[index])
    return extended


def classify(password: str, passwords: list[str]) -> str:
    """Визначити категорію надійності пароля.

    Перевірки впорядковані від найсуворішої до найм'якшої:
    категорії в умові перекриваються, тому результат визначає
    перший збіг у каскаді if/elif.
    """
    if is_forbidden(password):
        return "Заборонений"

    if meets_all_criteria(password):
        threshold = CRITERIA["min_length"] + VERY_STRONG_BONUS
        if len(password) >= threshold and is_unique(password, passwords):
            return "Дуже сильний"
        return "Сильний"

    if count_char_groups(password) >= MIDDLE_GROUPS:
        return "Середній"

    return "Слабкий"


def format_groups(password: str) -> str:
    """Скласти позначку наявних груп символів у вигляді dUl!."""
    marks = [
        "d" if has_digit(password) else "-",
        "U" if has_upper(password) else "-",
        "l" if has_lower(password) else "-",
        "!" if has_special(password) else "-",
    ]
    return "".join(marks)


def print_header() -> None:
    """Вивести шапку звіту з даними студента."""
    print("―" * 62)
    print("Лабораторна робота №1, завдання 1: аналіз паролів")
    print(f"Студент: {STUDENT_NAME}")
    print(f"Група:   {GROUP_NAME}")
    print(f"Варіант: {VARIANT_NUMBER}")
    print("―" * 62)


def print_table(passwords: list[str]) -> None:
    """Вивести таблицю результатів аналізу паролів."""
    header = f"{'№':<4}{'Пароль':<20}{'Дов.':>5}  {'dUl!':<7}{'Категорія':<14}"
    print(header)
    print("-" * 62)
    for number, password in enumerate(passwords, start=1):
        row = (
            f"{number:<4}{password:<20}{len(password):>5}  "
            f"{format_groups(password):<7}"
            f"{classify(password, passwords):<14}"
        )
        print(row)
    print("-" * 62)


def print_summary(passwords: list[str]) -> None:
    """Вивести кількість паролів за кожною категорією."""
    order = [
        "Заборонений",
        "Слабкий",
        "Середній",
        "Сильний",
        "Дуже сильний",
    ]
    categories = [classify(item, passwords) for item in passwords]
    print("Підсумок:")
    for category in order:
        print(f"  {category:<16}{categories.count(category):>3}")


def main() -> None:
    """Точка входу завдання 1."""
    print_header()
    extended = add_duplicates(PASSWORDS, DUPLICATES_COUNT)
    print(
        f"Імітація повторного використання: додано "
        f"{DUPLICATES_COUNT} дублікати, "
        f"{len(PASSWORDS)} -> {len(extended)} паролів.\n"
    )
    print_table(extended)
    print()
    print_summary(extended)


if __name__ == "__main__":
    main()
