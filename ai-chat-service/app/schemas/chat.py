"""Схемы запроса/ответа чата."""
from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    message: str
