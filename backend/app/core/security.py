import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Argon2id as primary, bcrypt as fallback for migrated passwords
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# Load RSA keys once at module level
_private_key: str | None = None
_public_key: str | None = None


def _load_keys() -> tuple[str, str]:
    global _private_key, _public_key
    if _private_key is None or _public_key is None:
        priv_path = Path(settings.JWT_PRIVATE_KEY_PATH)
        pub_path = Path(settings.JWT_PUBLIC_KEY_PATH)
        if not priv_path.exists() or not pub_path.exists():
            raise RuntimeError(
                f"JWT keys not found at {priv_path} / {pub_path}. "
                "Generate with: openssl genpkey -algorithm RSA -out keys/private.pem -pkeyopt rsa_keygen_bits:2048 "
                "&& openssl rsa -pubout -in keys/private.pem -out keys/public.pem"
            )
        _private_key = priv_path.read_text()
        _public_key = pub_path.read_text()
    return _private_key, _public_key


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Fallback to passlib for bcrypt migrated passwords
        return pwd_context.verify(password, hashed)


def needs_rehash(hashed: str) -> bool:
    return ph.check_needs_rehash(hashed)


def generate_refresh_token() -> tuple[str, str]:
    """Generate a UUID refresh token and its SHA-256 hash."""
    token = str(uuid.uuid4())
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token with SHA-256 for Redis storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(
    user_id: int,
    username: str,
    role_id: int | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    private_key, _ = _load_keys()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "username": username,
        "role_id": role_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate an access token. Raises JWTError on failure."""
    _, public_key = _load_keys()
    payload = jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload
