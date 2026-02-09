"""Эндпоинты чата."""
from fastapi import APIRouter, Depends, Header

from app.core.database import get_db
from app.schemas import ChatMessageIn, ChatMessageOut
from app.services import ChatService

router = APIRouter()

# Backend проксирует с заголовком User-ID
_USER_ID_HEADER = "User-ID"


@router.post("/", response_model=ChatMessageOut, summary="Отправить сообщение (эхо + сохранение в MongoDB)")
async def chat(
    body: ChatMessageIn,
    db=Depends(get_db),
    user_id: str | None = Header(None, alias=_USER_ID_HEADER),
):
    uid = user_id or "anonymous"
    message = await ChatService.echo(db, uid, body.message)
    return ChatMessageOut(message=message)
