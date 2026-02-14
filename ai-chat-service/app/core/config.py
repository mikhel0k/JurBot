"""Конфигурация ai-chat-service."""
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ai-chat-service
PROJECT_ROOT = BASE_DIR.parent  # JurBot
load_dotenv(dotenv_path=str(BASE_DIR / ".env"))
load_dotenv(dotenv_path=str(PROJECT_ROOT / ".env"))
load_dotenv(dotenv_path=str(PROJECT_ROOT / "backend" / ".env"))


class Settings(BaseSettings):
    API_TOKEN: str = ""

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "jurbot"

    model_config = SettingsConfigDict(from_attributes=True)


settings = Settings()
