"""Прокси запросов чата в AI-микросервис. Требует аутентификации (cookies)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import httpx

from app.core.config import settings
from app.core.dependencies import get_user_id

router = APIRouter(prefix="/chat", tags=["chat"])
_BASE = f"{settings.AI_CHAT_SERVICE_URL.rstrip('/')}/ai_chat/v1/chat"


class ChatMessageIn(BaseModel):
    message: str


def _headers(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


@router.post("", summary="Отправить сообщение в чат с ИИ")
async def chat(
    body: ChatMessageIn,
    user_id: int = Depends(get_user_id),
):
    url = f"{_BASE}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(url, json={"message": body.message}, headers=_headers(user_id))
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="AI chat service unavailable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/history", summary="История переписки с пагинацией")
async def get_chat_history(
    user_id: int = Depends(get_user_id),
    page: int = 1,
    page_size: int = 20,
):
    """Возвращает историю сообщений текущего пользователя (items, total, page, page_size)."""
    url = f"{_BASE}/history"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(url, params={"page": page, "page_size": page_size}, headers=_headers(user_id))
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="AI chat service unavailable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.get("/conversations", summary="Список всех переписок с пагинацией")
async def get_conversations(
    user_id: int = Depends(get_user_id),
    page: int = 1,
    page_size: int = 20,
):
    """Возвращает список всех чатов (user_id, updated_at, message_count) с пагинацией."""
    url = f"{_BASE}/conversations"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.get(url, params={"page": page, "page_size": page_size}, headers=_headers(user_id))
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="AI chat service unavailable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
