"""Головний файл лабораторної роботи №1.

Послідовно запускає демонстрацію всіх завдань варіанта.
"""

from collections.abc import Callable

import task1
import task2
import task3_v2

# import task3


def run_task(number: int, title: str, entry: Callable[[], None]) -> None:
    """Запустити одне завдання з роздільником і заголовком."""
    print(f"\n{'#' * 50}")
    print(f"#  ЗАВДАННЯ {number}: {title}")
    print(f"{'#' * 50}\n")
    entry()


def main() -> None:
    """Точка входу лабораторної роботи №1."""
    run_task(1, "Аналізатор надійності паролів", task1.main)
    run_task(2, "Система контролю доступу", task2.main)
    # run_task(3, "Хешування, CSV-база та JSON-логування", task3.main)
    run_task(4, "Оновлена версія завдання 3", task3_v2.main)


if __name__ == "__main__":
    main()
