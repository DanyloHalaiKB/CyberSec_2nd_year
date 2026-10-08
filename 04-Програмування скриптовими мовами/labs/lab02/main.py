"""Точка входу лабораторної роботи №2: команди demo та analyze.

Запуск з кореня репозиторію:
    python -m labs.lab02.main demo
    python -m labs.lab02.main analyze --activity-log <шлях> [--after-hours]
"""

import argparse
from collections.abc import Sequence

from labs.lab02 import task1, task2


def run_demo(args: argparse.Namespace) -> int:
    """Запускає демонстрацію завдання 1."""
    task1.demo()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Створює парсер із підкомандами demo та analyze."""
    parser = argparse.ArgumentParser(
        prog="python -m labs.lab02.main",
        description="ЛР №2: консольні утиліти для задач кібербезпеки.",
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="{demo,analyze}"
    )

    demo = subparsers.add_parser(
        "demo", help="завдання 1: демонстрація класів User/Admin/UserAccount"
    )
    demo.set_defaults(func=run_demo)

    analyze = subparsers.add_parser(
        "analyze",
        help="завдання 2 (варіант 7): аналіз журналу активності користувачів",
    )
    task2.add_arguments(analyze)
    analyze.set_defaults(func=task2.analyze)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Розбирає аргументи та виконує вибрану команду."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
