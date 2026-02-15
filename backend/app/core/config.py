from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CRM Protegrt API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database (via PgBouncer for app, direct for migrations)
    DATABASE_URL: str = "postgresql+asyncpg://protegrt:protegrt@localhost:6432/protegrt_db"
    DATABASE_URL_DIRECT: str = "postgresql+asyncpg://protegrt:protegrt@localhost:5433/protegrt_db"
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_PRIVATE_KEY_PATH: str = "keys/private.pem"
    JWT_PUBLIC_KEY_PATH: str = "keys/public.pem"
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS_WEB: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS_MOBILE: int = 30

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Rate Limiting
    LOGIN_RATE_LIMIT_USER: int = 5
    LOGIN_RATE_LIMIT_IP: int = 10
    LOGIN_RATE_LIMIT_WINDOW: int = 900  # 15 minutes in seconds
    LOGIN_LOCKOUT_ATTEMPTS: int = 10
    LOGIN_LOCKOUT_DURATION: int = 1800  # 30 minutes in seconds

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # WhatsApp (Evolution API)
    EVOLUTION_API_URL: str = ""
    EVOLUTION_API_KEY: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_ALERT_CHAT_ID: str = ""

    # Quotations (external API)
    QUOTATIONS_API_URL: str = "https://cotizaciones.protegrt.com/api/v1"
    QUOTATIONS_API_KEY: str = ""
    QUOTATIONS_API_TIMEOUT: int = 10

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()
