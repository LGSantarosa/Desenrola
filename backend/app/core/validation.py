import re
from datetime import date

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def only_digits(value):
    return re.sub(r"\D", "", value or "")


def is_valid_name(name):
    return len((name or "").strip()) >= 5


def is_valid_email(email):
    return bool(email and EMAIL_RE.match(email.strip()))


def is_strong_password(password):
    if not password or len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special


def is_valid_cpf(cpf):
    digits = only_digits(cpf)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    for length in (9, 10):
        total = sum(int(digits[i]) * (length + 1 - i) for i in range(length))
        check = (total * 10) % 11
        if check == 10:
            check = 0
        if check != int(digits[length]):
            return False
    return True


def is_valid_phone(phone):
    digits = only_digits(phone)
    if len(digits) != 11:
        return False
    ddd = int(digits[:2])
    return 11 <= ddd <= 99


def is_valid_birth_date(value):
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except ValueError:
            return False
    today = date.today()
    if value >= today:
        return False
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    return age >= 16
