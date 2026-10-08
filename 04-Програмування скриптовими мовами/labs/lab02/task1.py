"""Завдання 1: модель користувача, сеансу, журналу аудиту та акаунта.

Класи:
    User         - користувач із безпечним зберіганням пароля (PBKDF2);
    Admin        - адміністратор (наслідування від User);
    Session      - сеанс роботи з відліком неактивності;
    AuditEntry   - окремий запис журналу (@dataclass);
    AuditLog     - журнал аудиту;
    UserAccount  - акаунт (композиція User + Session + AuditLog).

Демонстрація запускається функцією demo() (python -m labs.lab02.main demo)
і не виконується під час імпорту модуля.
"""

import hashlib
import hmac
import ipaddress
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# Параметри хешування пароля (PBKDF2-HMAC-SHA256)
PBKDF2_HASH_NAME = "sha256"
PBKDF2_ITERATIONS = 600_000
SALT_SIZE_BYTES = 16
MIN_PASSWORD_LENGTH = 8

# Час життя сеансу без активності (секунди)
SESSION_TIMEOUT_SEC = 900

# Email: локальна частина починається з латинської літери, всього 3-64
# символів (латиниця, цифри, "_"), далі "@" і домен щонайменше з однією
# крапкою. Це спрощена перевірка заданого формату, а не повний RFC 5322.
_DOMAIN_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
EMAIL_PATTERN = re.compile(
    rf"[A-Za-z][A-Za-z0-9_]{{2,63}}@{_DOMAIN_LABEL}(?:\.{_DOMAIN_LABEL})+"
)


def _utc_now() -> datetime:
    """Повертає поточний час UTC з часовим поясом."""
    return datetime.now(timezone.utc)


class User:
    """Користувач системи. Пароль зберігається лише як PBKDF2-хеш із сіллю."""

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "user",
        active: bool = True,
    ) -> None:
        """Створює користувача та одразу хешує переданий пароль."""
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Ім'я користувача не може бути порожнім.")
        self.username = username
        self.email = email  # проходить перевірку у setter-і властивості
        self.role = role
        self.active = active
        # Приватні атрибути: Python перейменовує їх (name mangling) на
        # _User__password_hash та _User__password_salt.
        self.__password_hash = b""
        self.__password_salt = b""
        self.set_password(password)

    @property
    def email(self) -> str:
        """Повертає email користувача."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Встановлює email після перевірки за допомогою регулярного виразу."""
        if not isinstance(value, str) or not EMAIL_PATTERN.fullmatch(value):
            raise ValueError(f"Некоректний email: {value!r}")
        self._email = value

    @staticmethod
    def _derive_hash(password: str, salt: bytes) -> bytes:
        """Обчислює PBKDF2-HMAC-SHA256 для пароля та солі."""
        return hashlib.pbkdf2_hmac(
            PBKDF2_HASH_NAME,
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )

    def set_password(self, password: str) -> None:
        """Генерує нову випадкову сіль і зберігає хеш нового пароля."""
        if (
            not isinstance(password, str)
            or len(password) < MIN_PASSWORD_LENGTH
        ):
            raise ValueError(
                "Пароль має містити щонайменше "
                f"{MIN_PASSWORD_LENGTH} символів."
            )
        salt = os.urandom(SALT_SIZE_BYTES)
        self.__password_salt = salt
        self.__password_hash = self._derive_hash(password, salt)

    def check_password(self, password: str) -> bool:
        """Перевіряє пароль у сталий час (hmac.compare_digest)."""
        if not isinstance(password, str):
            return False
        candidate = self._derive_hash(password, self.__password_salt)
        return hmac.compare_digest(candidate, self.__password_hash)

    def deactivate(self) -> None:
        """Деактивує обліковий запис."""
        self.active = False

    def _fields(self) -> str:
        """Формує безпечний опис полів (без пароля, хешу та солі)."""
        return (
            f"username={self.username!r}, email={self.email!r}, "
            f"role={self.role!r}, active={self.active}"
        )

    def __str__(self) -> str:
        """Повертає текстовий опис користувача."""
        return f"User({self._fields()})"


class Admin(User):
    """Адміністратор: користувач (Is-A) із набором дозволів."""

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        permissions: Iterable[str] | None = None,
        active: bool = True,
    ) -> None:
        """Створює адміністратора; кожен екземпляр має власну множину прав."""
        super().__init__(
            username, email, password, role="admin", active=active
        )
        self.permissions: set[str] = set()
        for permission in permissions or ():
            self.grant_permission(permission)

    def grant_permission(self, permission: str) -> None:
        """Додає дозвіл."""
        if not isinstance(permission, str) or not permission.strip():
            raise ValueError("Назва дозволу не може бути порожньою.")
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        """Забирає дозвіл (якщо його не було - нічого не робить)."""
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        """Перевіряє наявність дозволу."""
        return permission in self.permissions

    def __str__(self) -> str:
        """Повертає опис адміністратора разом із його дозволами."""
        return (
            f"Admin({self._fields()}, permissions={sorted(self.permissions)})"
        )


class Session:
    """Сеанс користувача: IP, час входу та остання активність (UTC)."""

    def __init__(self, ip: str) -> None:
        """Створює сеанс; некоректна IP-адреса дає ValueError."""
        ipaddress.ip_address(ip)
        now = _utc_now()
        self.ip = ip
        self.login_time = now
        self.last_activity = now

    def touch(self) -> None:
        """Оновлює час останньої активності."""
        self.last_activity = _utc_now()

    def is_active(self, timeout_sec: int) -> bool:
        """Повертає True, якщо з останньої активності минуло менше timeout."""
        if timeout_sec <= 0:
            raise ValueError("timeout_sec має бути додатним числом.")
        idle = _utc_now() - self.last_activity
        return idle < timedelta(seconds=timeout_sec)


@dataclass(frozen=True)
class AuditEntry:
    """Незмінний запис журналу аудиту (час UTC, користувач, дія)."""

    timestamp: datetime
    username: str
    action: str

    def __str__(self) -> str:
        """Повертає запис у вигляді одного рядка."""
        return (
            f"{self.timestamp:%Y-%m-%d %H:%M:%S} UTC | "
            f"{self.username:<10} | {self.action}"
        )


class AuditLog:
    """Журнал аудиту. Паролі в журнал не записуються."""

    def __init__(self) -> None:
        """Створює порожній журнал."""
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        """Повертає копію записів лише для читання."""
        return tuple(self._entries)

    def add_log(self, username: str, action: str) -> AuditEntry:
        """Додає запис (login_success, login_failure, logout, ...)."""
        entry = AuditEntry(_utc_now(), username, action)
        self._entries.append(entry)
        return entry

    def show_all(self) -> None:
        """Друкує всі записи журналу."""
        if not self._entries:
            print("(журнал порожній)")
        for entry in self._entries:
            print(entry)


class UserAccount:
    """Акаунт: композиція (Has-A) User, Session та AuditLog."""

    # Дозволені ключі: ключ -> (назва атрибута, допустимі типи).
    # Хеш і сіль пароля через ключі недоступні.
    _ITEMS: dict[str, tuple[str, tuple[type, ...]]] = {
        "user": ("user", (User,)),
        "session": ("session", (Session, type(None))),
        "audit_log": ("audit_log", (AuditLog,)),
    }

    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
        timeout_sec: int = SESSION_TIMEOUT_SEC,
    ) -> None:
        """Об'єднує переданих (або нових) User, Session та AuditLog."""
        if timeout_sec <= 0:
            raise ValueError("timeout_sec має бути додатним числом.")
        self.timeout_sec = timeout_sec
        self["user"] = user
        self["session"] = session
        self["audit_log"] = AuditLog() if audit_log is None else audit_log

    def login(self, username: str, password: str, ip: str) -> bool:
        """Автентифікує користувача й створює сеанс лише після успіху."""
        # Пароль перевіряється завжди, щоб час відповіді не залежав від
        # того, чи існує такий логін.
        password_ok = self.user.check_password(password)
        if not (
            password_ok and self.user.active and username == self.user.username
        ):
            self.audit_log.add_log(str(username), "login_failure")
            return False
        session = Session(ip)
        session.touch()
        self.session = session
        self.audit_log.add_log(username, "login_success")
        return True

    def is_authenticated(self) -> bool:
        """Перевіряє, що сеанс існує, не прострочений і користувач активний.

        Успішна перевірка продовжує сеанс (touch), невдала - ні.
        """
        if self.session is None:
            return False
        if not self.user.active:
            self.audit_log.add_log(self.user.username, "session_revoked")
            self.session = None
            return False
        if self.session.is_active(self.timeout_sec):
            self.session.touch()
            return True
        self.audit_log.add_log(self.user.username, "session_timeout")
        self.session = None
        return False

    def logout(self) -> bool:
        """Завершує сеанс і фіксує подію; False, якщо сеансу не було."""
        if self.session is None:
            return False
        self.audit_log.add_log(self.user.username, "logout")
        self.session = None
        return True

    def __getitem__(self, key: str) -> User | Session | AuditLog | None:
        """Повертає дозволений атрибут: account["user"], ["session"], ..."""
        if key not in self._ITEMS:
            raise KeyError(key)
        return getattr(self, self._ITEMS[key][0])

    def __setitem__(self, key: str, value: object) -> None:
        """Записує дозволений атрибут із перевіркою типу."""
        if key not in self._ITEMS:
            raise KeyError(key)
        attr, allowed_types = self._ITEMS[key]
        if not isinstance(value, allowed_types):
            names = " або ".join(
                "None" if t is type(None) else t.__name__
                for t in allowed_types
            )
            raise TypeError(
                f"Для ключа {key!r} очікується {names}, "
                f"отримано {type(value).__name__}."
            )
        setattr(self, attr, value)


def _section(title: str) -> None:
    """Друкує заголовок розділу демонстрації."""
    print(f"\n——— {title} ———")


def demo() -> None:
    """Демонструє роботу всіх класів завдання 1."""
    _section("1. Створення користувачів")
    admin = Admin(
        "admin_olga",
        "olga_admin@corp.example.com",
        "S3cure!Passw0rd",
        permissions={"read_logs"},
    )
    print(admin)
    print("Хеш пароля зберігається приватно (name mangling):")
    print(" ", [name for name in vars(admin) if "password" in name])

    account = UserAccount(admin)

    _section("2. Вхід: невдалий і успішний")
    ok = account.login("admin_olga", "wrong-password", "10.0.0.5")
    print(f"Невдалий вхід (хибний пароль): {ok}")
    print(f"is_authenticated: {account.is_authenticated()}")
    ok = account.login("admin_olga", "S3cure!Passw0rd", "10.0.0.5")
    print(f"Успішний вхід: {ok}")
    print(f"is_authenticated: {account.is_authenticated()}")
    print(f"IP сеансу: {account['session'].ip}")

    _section("3. Зміна email із валідацією")
    admin.email = "olga_new@corp.example.com"
    print(f"Новий email: {admin.email}")
    for bad_email in ("1olga@corp.example.com", "ol@corp.example.com", "a@b"):
        try:
            admin.email = bad_email
        except ValueError as error:
            print(f"ValueError: {error}")

    _section("4. Права адміністратора")
    admin.grant_permission("manage_users")
    print(f"manage_users: {admin.has_permission('manage_users')}")
    admin.revoke_permission("manage_users")
    print(f"manage_users після revoke: {admin.has_permission('manage_users')}")
    print(admin)

    _section("5. Доступ до атрибутів через [] (__getitem__/__setitem__)")
    print(f"account['user'] -> {account['user']}")
    for key in ("password_hash", "unknown"):
        try:
            account[key]
        except KeyError as error:
            print(f"KeyError: ключ {error} недоступний")
    try:
        account["session"] = "не сеанс"
    except TypeError as error:
        print(f"TypeError: {error}")

    _section("6. Завершення сеансу за таймаутом (імітація)")
    session = account["session"]
    session.last_activity -= timedelta(seconds=SESSION_TIMEOUT_SEC + 1)
    print(f"Минуло {SESSION_TIMEOUT_SEC + 1} с без активності")
    print(f"is_authenticated: {account.is_authenticated()}")

    _section("7. Повторний вхід і вихід із системи")
    print(
        f"Вхід: {account.login('admin_olga', 'S3cure!Passw0rd', '10.0.0.5')}"
    )
    print(f"Вихід: {account.logout()}")
    print(f"is_authenticated: {account.is_authenticated()}")

    _section("8. Журнал аудиту")
    account["audit_log"].show_all()


if __name__ == "__main__":
    demo()
