"""Завдання 2: багаторівнева система контролю доступу."""

# ANSI escape-коди для кольорів у терміналі
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

# Вхідні дані (Варіант 7)
users = {
    "incident_commander": {
        "role": "incident_response",
        "clearance": 4,
        "department": "CSIRT",
        "active": True,
    },
    "malware_analyst": {
        "role": "malware_researcher",
        "clearance": 3,
        "department": "Research",
        "active": True,
    },
    "monitoring_tech": {
        "role": "monitoring",
        "clearance": 2,
        "department": "NOC",
        "active": True,
    },
    "customer_rep": {
        "role": "customer_service",
        "clearance": 1,
        "department": "Customer",
        "active": True,
    },
    "backup_service": {
        "role": "service_account",
        "clearance": 2,
        "department": "System",
        "active": False,
    },
}

resources = [
    ("incident_playbook", 4),
    ("malware_lab", 3),
    ("monitoring_dashboards", 2),
    ("customer_portal", 1),
    ("emergency_procedures", 4),
    ("service_desk", 1),
    ("reverse_engineering", 3),
    ("alert_systems", 2),
    ("escalation_matrix", 3),
    ("knowledge_base", 1),
]

security_levels = ("Public Access", "Authorized", "Privileged", "Critical")

blocked_users = {"backup_service", "deactivated_svc", "policy_violation"}


def check_access(username: str, resource: str, res_level: int) -> str:
    """Перевіряє рівень доступу користувача до визначеного ресурсу."""
    if username not in users:
        return "DENY (User not found)"

    if username in blocked_users:
        return "DENY (User is blocked)"

    user_info = users[username]

    if not user_info.get("active"):
        return "DENY (Account inactive)"

    if user_info.get("clearance", 0) >= res_level:
        return "ALLOW"

    return "DENY (Insufficient clearance)"


def main() -> None:
    """Головна функція для ініціалізації перевірки доступу."""
    print("Список ресурсів системи:")
    for res_name, res_level in resources:
        level_name = security_levels[res_level - 1]
        print(f"- {res_name}: {level_name}")

    print("Результати перевірки доступу:")

    # Додаємо фіктивного користувача для тестування (User not found)
    users_to_test = list(users.keys()) + ["unknown_guest"]

    # Перевірка доступу кожного користувача до кожного ресурсу
    for username in users_to_test:
        for res_name, res_level in resources:
            decision = check_access(username, res_name, res_level)

            if decision.startswith("ALLOW"):
                colored_decision = f"{COLOR_GREEN}{decision}{COLOR_RESET}"
            else:
                colored_decision = f"{COLOR_RED}{decision}{COLOR_RESET}"

            print(
                f"user = {username} resource = {res_name} > {colored_decision}"
            )
        print("—" * 50)


if __name__ == "__main__":
    main()
