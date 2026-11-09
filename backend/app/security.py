from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

from app.config import settings

if settings.hash_scheme != "argon2id":
    raise RuntimeError("поддерживается только HASH_SCHEME=argon2id")

_hasher = PasswordHasher(
    time_cost=settings.argon2_time_cost,
    memory_cost=settings.argon2_memory_cost,
    parallelism=settings.argon2_parallelism,
    type=Type.ID,
)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False
