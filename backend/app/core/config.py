"""Конфигурация приложения. Единая точка импорта: from app.core.config import settings."""
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=str(BASE_DIR / ".env"))


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    POSTGRES_DB_TEST: Optional[str] = None
    POSTGRES_USER_TEST: Optional[str] = None
    POSTGRES_PASSWORD_TEST: Optional[str] = None
    POSTGRES_HOST_TEST: Optional[str] = None
    POSTGRES_PORT_TEST: Optional[int] = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    API_TOKEN: str

    LOG_LEVEL: str = "INFO"

    JWT_PRIVATE_KEY: Path = BASE_DIR / "jwt_tokens" / "jwt-private.pem"
    JWT_PUBLIC_KEY: Path = BASE_DIR / "jwt_tokens" / "jwt-public.pem"
    ALGORITHM: str = "RS256"

    LOGIN_FOR_GMAIL: str = ""
    PASSWORD_FOR_GMAIL: str = ""

    SEND_LOGIN_CODE_EMAIL: bool = True

    ENVIRONMENT: str = "production"

    CORS_ORIGINS: str = ""

    AI_CHAT_SERVICE_URL: str = "http://localhost:8001"

    MONGO_URI: str = "mongodb://localhost:27017"

    @property
    def SECURE_COOKIES(self) -> bool:
        """False в development для работы cookies по HTTP (localhost)."""
        return self.ENVIRONMENT != "development"

    @property
    def DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")

    def _test_db(self) -> str:
        return self.POSTGRES_DB_TEST or self.POSTGRES_DB

    def _test_user(self) -> str:
        return self.POSTGRES_USER_TEST or self.POSTGRES_USER

    def _test_password(self) -> str:
        return self.POSTGRES_PASSWORD_TEST or self.POSTGRES_PASSWORD

    def _test_host(self) -> str:
        return self.POSTGRES_HOST_TEST or self.POSTGRES_HOST

    def _test_port(self) -> int:
        return self.POSTGRES_PORT_TEST if self.POSTGRES_PORT_TEST is not None else self.POSTGRES_PORT

    @property
    def TEST_DATABASE_URL(self) -> str:
        return (f"postgresql+asyncpg://{self._test_user()}:{self._test_password()}@"
                f"{self._test_host()}:{self._test_port()}/{self._test_db()}")

    @property
    def TEST_SYNC_DATABASE_URL(self) -> str:
        return (f"postgresql://{self._test_user()}:{self._test_password()}@"
                f"{self._test_host()}:{self._test_port()}/{self._test_db()}")

    model_config = SettingsConfigDict(from_attributes=True)


settings = Settings()
