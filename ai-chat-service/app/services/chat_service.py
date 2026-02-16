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


async def get_history_paginated(
    db: AsyncIOMotorDatabase[Any],
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """История переписки пользователя с пагинацией. page 1-based."""
    skip = max(0, (page - 1) * page_size)
    page_size = max(1, min(page_size, 100))
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$facet": {
                "total": [{"$count": "count"}],
                "messages": [
                    {
                        "$project": {
                            "messages": {"$slice": ["$messages", skip, page_size]},
                        },
                    },
                ],
            },
        },
    ]
    cursor = db[CHAT_COLLECTION].aggregate(pipeline)
    doc = await cursor.to_list(length=1)
    if not doc or not doc[0]:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    total = doc[0]["total"][0]["count"] if doc[0]["total"] else 0
    messages_raw = doc[0]["messages"][0]["messages"] if doc[0]["messages"] else []
    items = [
        {
            "role": m["role"],
            "content": m["content"],
            "created_at": m.get("created_at"),
        }
        for m in messages_raw
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def get_all_conversations_paginated(
    db: AsyncIOMotorDatabase[Any],
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Список всех переписок (по user_id) с пагинацией. page 1-based."""
    skip = max(0, (page - 1) * page_size)
    page_size = max(1, min(page_size, 100))
    pipeline = [
        {"$match": {}},
        {"$sort": {"updated_at": -1}},
        {
            "$facet": {
                "total": [{"$count": "count"}],
                "chats": [
                    {"$skip": skip},
                    {"$limit": page_size},
                    {
                        "$project": {
                            "user_id": 1,
                            "updated_at": 1,
                            "message_count": {"$size": {"$ifNull": ["$messages", []]}},
                        },
                    },
                ],
            },
        },
    ]
    cursor = db[CHAT_COLLECTION].aggregate(pipeline)
    doc = await cursor.to_list(length=1)
    if not doc or not doc[0]:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    total = doc[0]["total"][0]["count"] if doc[0]["total"] else 0
    items = [
        {
            "user_id": c["user_id"],
            "updated_at": c.get("updated_at"),
            "message_count": c.get("message_count", 0),
        }
        for c in doc[0]["chats"]
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


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
