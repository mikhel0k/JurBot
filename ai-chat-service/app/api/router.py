"""Роутер API: подключение версий."""
from fastapi import APIRouter

from app.api.v1.Chat import router as chat_router

router = APIRouter()
router.include_router(chat_router, prefix="/v1", tags=["chat"])
