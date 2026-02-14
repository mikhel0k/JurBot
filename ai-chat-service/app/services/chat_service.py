"""Сохранение и загрузка истории чата по user_id в MongoDB."""
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


CHAT_COLLECTION = "chats"


async def get_history(db: AsyncIOMotorDatabase[Any], user_id: int) -> list[dict[str, str]]:
    """Возвращает историю сообщений пользователя в формате [{role, content}, ...] для OpenAI."""
    doc = await db[CHAT_COLLECTION].find_one({"user_id": user_id})
    if not doc or "messages" not in doc:
        return []
    return [{"role": m["role"], "content": m["content"]} for m in doc["messages"]]


async def add_messages(
    db: AsyncIOMotorDatabase[Any],
    user_id: int,
    messages: list[dict[str, str]],
) -> None:
    """Добавляет сообщения в историю чата пользователя."""
    now = datetime.now(timezone.utc)
    entries = [{"role": m["role"], "content": m["content"], "created_at": now} for m in messages]
    await db[CHAT_COLLECTION].update_one(
        {"user_id": user_id},
        {
            "$push": {"messages": {"$each": entries}},
            "$set": {"updated_at": now},
        },
        upsert=True,
    )
