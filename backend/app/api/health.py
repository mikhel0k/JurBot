"""Health check эндпоинты для load balancer и Kubernetes."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.redis import get_redis

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness")
async def health():
    """Проверка, что приложение запущено. Для Kubernetes liveness probe."""
    return {"status": "ok"}


@router.get("/ready", summary="Readiness")
async def ready(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """Проверка готовности к приёму трафика: PostgreSQL и Redis доступны."""
    try:
        await session.execute(text("SELECT 1"))
        await redis.ping()
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})
