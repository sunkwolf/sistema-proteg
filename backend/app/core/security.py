import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Argon2id as primary, bcrypt as fallback for migrated passwords
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        # Try Argon2id first
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


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    # Read private key
    with open(settings.JWT_PRIVATE_KEY_PATH) as f:
        private_key = f.read()

    return jwt.encode(to_encode, private_key, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    with open(settings.JWT_PUBLIC_KEY_PATH) as f:
        public_key = f.read()

    return jwt.decode(token, public_key, algorithms=[settings.JWT_ALGORITHM])
