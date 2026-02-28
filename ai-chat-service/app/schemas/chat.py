"""Схемы запроса/ответа чата."""
from datetime import datetime
from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    message: str
    chat_id: str | None = None  # если нет — создаётся новый чат


class ChatMessageOut(BaseModel):
    message: str


class MessageItem(BaseModel):
    role: str
    content: str
    created_at: datetime | None = None


class HistoryPaginatedOut(BaseModel):
    items: list[MessageItem]
    total: int
    page: int
    page_size: int


class ConversationItem(BaseModel):
    chat_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    message_count: int


class ConversationsPaginatedOut(BaseModel):
    items: list[ConversationItem]
    total: int
    page: int
    page_size: int
