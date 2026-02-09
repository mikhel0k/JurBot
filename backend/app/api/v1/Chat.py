"""Прокси запросов чата в AI-микросервис. Требует аутентификации (cookies)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import httpx

from app.core.config import settings
from app.core.dependencies import get_user_id

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessageIn(BaseModel):
    message: str


@router.post("/", summary="Отправить сообщение в чат с ИИ")
async def chat(
    body: ChatMessageIn,
    user_id: int = Depends(get_user_id),
):
    url = f"{settings.AI_CHAT_SERVICE_URL.rstrip('/')}/ai_chat/v1/"
    headers = {"User-ID": str(user_id)}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(url, json={"message": body.message}, headers=headers)
            r.raise_for_status()
            return r.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="AI chat service unavailable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
