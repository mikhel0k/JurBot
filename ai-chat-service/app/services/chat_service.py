"""Сохранение и загрузка чатов в MongoDB. Один документ = один чат (user_id + _id как chat_id)."""
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


CHAT_COLLECTION = "chats"


def _check_chat_owner(doc: dict | None, user_id: int) -> bool:
    """Проверяет, что чат принадлежит пользователю."""
    return doc is not None and doc.get("user_id") == user_id


async def create_chat(db: AsyncIOMotorDatabase[Any], user_id: int) -> str:
    """Создаёт новый чат для пользователя. Возвращает chat_id (str)."""
    now = datetime.now(timezone.utc)
    result = await db[CHAT_COLLECTION].insert_one(
        {
            "user_id": user_id,
            "messages": [],
            "created_at": now,
            "updated_at": now,
        }
    )
    return str(result.inserted_id)


async def get_history(db: AsyncIOMotorDatabase[Any], user_id: int, chat_id: str) -> list[dict[str, str]]:
    """Возвращает историю сообщений чата в формате [{role, content}, ...] для OpenAI.
    Проверяет, что чат принадлежит user_id. Если чат не найден или не его — пустой список."""
    try:
        oid = ObjectId(chat_id)
    except Exception:
        return []
    doc = await db[CHAT_COLLECTION].find_one({"_id": oid})
    if not _check_chat_owner(doc, user_id) or "messages" not in doc:
        return []
    return [{"role": m["role"], "content": m["content"]} for m in doc["messages"]]


async def get_history_paginated(
    db: AsyncIOMotorDatabase[Any],
    user_id: int,
    chat_id: str,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """История переписки в конкретном чате с пагинацией. page 1-based. Только свой чат."""
    try:
        oid = ObjectId(chat_id)
    except Exception:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    skip = max(0, (page - 1) * page_size)
    page_size = max(1, min(page_size, 100))
    doc = await db[CHAT_COLLECTION].find_one({"_id": oid, "user_id": user_id})
    if not doc or "messages" not in doc:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}
    messages = doc["messages"]
    total = len(messages)
    slice_messages = messages[skip : skip + page_size]
    items = [
        {"role": m["role"], "content": m["content"], "created_at": m.get("created_at")}
        for m in slice_messages
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def get_all_conversations_paginated(
    db: AsyncIOMotorDatabase[Any],
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Список чатов только текущего пользователя с пагинацией. page 1-based."""
    skip = max(0, (page - 1) * page_size)
    page_size = max(1, min(page_size, 100))
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$sort": {"updated_at": -1}},
        {
            "$facet": {
                "total": [{"$count": "count"}],
                "chats": [
                    {"$skip": skip},
                    {"$limit": page_size},
                    {
                        "$project": {
                            "chat_id": {"$toString": "$_id"},
                            "created_at": 1,
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
            "chat_id": c["chat_id"],
            "created_at": c.get("created_at"),
            "updated_at": c.get("updated_at"),
            "message_count": c.get("message_count", 0),
        }
        for c in doc[0]["chats"]
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def add_messages(
    db: AsyncIOMotorDatabase[Any],
    user_id: int,
    chat_id: str,
    messages: list[dict[str, str]],
) -> None:
    """Добавляет сообщения в чат. Проверяет, что чат принадлежит user_id. Иначе HTTP 404/403 — вызывающий слой решит."""
    try:
        oid = ObjectId(chat_id)
    except Exception:
        raise ValueError("invalid chat_id")
    now = datetime.now(timezone.utc)
    entries = [{"role": m["role"], "content": m["content"], "created_at": now} for m in messages]
    result = await db[CHAT_COLLECTION].update_one(
        {"_id": oid, "user_id": user_id},
        {
            "$push": {"messages": {"$each": entries}},
            "$set": {"updated_at": now},
        },
    )
    if result.matched_count == 0:
        raise ValueError("chat not found or access denied")
