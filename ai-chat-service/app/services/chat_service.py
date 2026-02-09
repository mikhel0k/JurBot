"""Сервис чата: сохранение сообщений и эхо."""
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class ChatService:
    """Эхо-чат с записью в MongoDB."""

    @staticmethod
    async def echo(db: AsyncIOMotorDatabase[Any], user_id: str, message: str) -> str:
        await db.messages.insert_one({
            "user_id": user_id,
            "message": message,
            "created_at": datetime.utcnow(),
        })
        return message
