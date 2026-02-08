"""Конфигурация приложения. Единая точка импорта: from app.core.config import settings."""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень backend (родитель каталога app: core -> app -> backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=str(BASE_DIR / ".env"))


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    POSTGRES_DB_TEST: str
    POSTGRES_USER_TEST: str
    POSTGRES_PASSWORD_TEST: str
    POSTGRES_HOST_TEST: str
    POSTGRES_PORT_TEST: int

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    LOG_LEVEL: str

    JWT_PRIVATE_KEY: Path = BASE_DIR / "jwt_tokens" / "jwt-private.pem"
    JWT_PUBLIC_KEY: Path = BASE_DIR / "jwt_tokens" / "jwt-public.pem"
    ALGORITHM: str = "RS256"

    LOGIN_FOR_GMAIL: str
    PASSWORD_FOR_GMAIL: str

    SEND_LOGIN_CODE_EMAIL: bool = True

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def TEST_DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER_TEST}:{self.POSTGRES_PASSWORD_TEST}@"
                f"{self.POSTGRES_HOST_TEST}:{self.POSTGRES_PORT_TEST}/{self.POSTGRES_DB_TEST}")

    @property
    def TEST_SYNC_DATABASE_URL(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER_TEST}:{self.POSTGRES_PASSWORD_TEST}@"
                f"{self.POSTGRES_HOST_TEST}:{self.POSTGRES_PORT_TEST}/{self.POSTGRES_DB_TEST}")

    model_config = SettingsConfigDict(from_attributes=True)


settings = Settings()
