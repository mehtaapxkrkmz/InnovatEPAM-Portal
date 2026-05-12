import hashlib
import hmac
import secrets

from passlib.context import CryptContext

from app.core.config import get_settings


def _build_pwd_context() -> CryptContext:
    settings = get_settings()
    return CryptContext(schemes=list(settings.bcrypt_schemes), deprecated="auto")


pwd_context = _build_pwd_context()


def hash_password(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback for environments with bcrypt backend incompatibilities.
        salt = secrets.token_hex(16)
        digest = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
        return f"sha256${salt}${digest}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("sha256$"):
        try:
            _, salt, digest = hashed_password.split("$", maxsplit=2)
        except ValueError:
            return False
        check = hashlib.sha256(f"{salt}{plain_password}".encode("utf-8")).hexdigest()
        return hmac.compare_digest(check, digest)

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False
