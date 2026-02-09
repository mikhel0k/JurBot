"""MongoDB: подключение и зависимость get_db для FastAPI."""
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

_client: AsyncIOMotorClient | None = None


async def init_mongodb() -> AsyncIOMotorClient:
    global _client
    _client = AsyncIOMotorClient(settings.MONGO_URI)
    return _client


async def close_mongodb() -> None:
    global _client
    if _client:
        _client.close()
        _client = None


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    if _client is None:
        raise RuntimeError("MongoDB not initialized")
    yield _client[settings.MONGO_DB]
