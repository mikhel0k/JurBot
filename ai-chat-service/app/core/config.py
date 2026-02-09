"""Конфигурация. Единая точка: from app.core.config import settings."""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=str(BASE_DIR / ".env"))


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "jurbot_chat"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
