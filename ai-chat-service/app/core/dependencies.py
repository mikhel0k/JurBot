"""Зависимости для эндпоинтов. user_id приходит в заголовке от backend."""
from fastapi import Depends, Header, HTTPException


async def get_user_id(x_user_id: str | None = Header(None, alias="X-User-Id")) -> int:
    """Читает user_id из заголовка X-User-Id (backend передаёт при вызове сервиса)."""
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id")
