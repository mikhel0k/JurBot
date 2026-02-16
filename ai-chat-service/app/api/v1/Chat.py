from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from openai import OpenAI
from openai import AuthenticationError as OpenAIAuthError

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_user_id
from app.schemas.chat import (
    ChatMessageIn,
    ConversationsPaginatedOut,
    HistoryPaginatedOut,
)
from app.services import (
    add_messages,
    get_all_conversations_paginated,
    get_history,
    get_history_paginated,
)

client = OpenAI(api_key=settings.API_TOKEN or "dummy")

SYSTEM_PROMPT = "Ты профессиональный юрист, который помогает малым и средним предприятиям разобраться в юридических вопросах."

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatMessageIn,
    user_id: int = Depends(get_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not settings.API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Set API_TOKEN in ai-chat-service .env",
        )
    history = await get_history(db, user_id)
    messages_for_api = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": request.message},
    ]
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
        )
    except OpenAIAuthError as e:
        raise HTTPException(status_code=503, detail="OpenAI API key invalid or missing") from e
    response_text = completion.choices[0].message.content if completion.choices else ""
    await add_messages(
        db,
        user_id,
        [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": response_text},
        ],
    )
    return {
        "response": response_text,
        "user": user_id,
    }


@router.get("/chat/history", response_model=HistoryPaginatedOut)
async def get_chat_history(
    user_id: int = Depends(get_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """Получение истории переписки текущего пользователя с пагинацией."""
    return await get_history_paginated(db, user_id, page=page, page_size=page_size)


@router.get("/chat/conversations", response_model=ConversationsPaginatedOut)
async def get_conversations(
    user_id: int = Depends(get_user_id),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    """Получение списка всех переписок с пагинацией (требуется заголовок X-User-Id)."""
    return await get_all_conversations_paginated(db, page=page, page_size=page_size)
