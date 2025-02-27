from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

__all__ = ["hash", "verify"]


def hash(value: str) -> str:
    ph = PasswordHasher()
    return ph.hash(value)


def verify(h: str, value: str) -> bool:
    ph = PasswordHasher()
    try:
        return ph.verify(h, value)
    except VerificationError:
        return False
