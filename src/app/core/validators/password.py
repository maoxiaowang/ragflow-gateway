import re
from functools import partial

from pydantic_core import PydanticCustomError

from app.core.settings import settings

COMPLEXITY_RULES = {
    "LOW": {
        "uppercase": False,
        "lowercase": False,
        "digits": False,
        "symbols": False,
        "min_length": 6
    },
    "MEDIUM": {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "symbols": False,
        "min_length": 6
    },
    "HIGH": {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "symbols": True,
        "min_length": 8
    }
}

PasswordError = partial(PydanticCustomError, "password_complexity")
SYMBOLS = r"!@#$%^&*()_+-=[]{}|;:'\",.<>?/"


def get_password_rules():
    return COMPLEXITY_RULES[settings.password_complexity]


def validate_complexity(v: str) -> str:
    rules = get_password_rules()
    errors = list()
    if len(v) < rules["min_length"]:
        errors.append(f"Password must be at least {rules["min_length"]} characters long")
    if rules["uppercase"] and not re.search(r"[A-Z]", v):
        errors.append("Password must contain at least one uppercase letter")
    if rules["lowercase"] and not re.search(r"[a-z]", v):
        errors.append("Password must contain at least one lowercase letter")
    if rules["digits"] and not re.search(r"[0-9]", v):
        errors.append("Password must contain at least one digit")
    if rules["symbols"] and not re.search(rf"[{re.escape(SYMBOLS)}]", v):
        errors.append("Password must contain at least one symbol")
    if errors:
        raise PasswordError(", ".join(errors))
    return v
