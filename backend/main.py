"""JurBot API — управление компаниями и сотрудниками."""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app import router
from app.core.config import settings
from app.core.rate_limit import limiter
from app.api.health import router as health_router
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis
from app.core.security import _get_jwt_private_key, _get_jwt_public_key

setup_logging()
logger = get_logger(__name__)

OPENAPI_DESCRIPTION = """
## Аутентификация

API использует **JWT в httponly cookies**:
- `access_token` — короткоживущий (30 мин)
- `refresh_token` — долгоживущий (30 дней)

Эндпоинты `/company/*` и `/employee/*` требуют аутентификации.
Cookies устанавливаются автоматически при `register/confirm` и `login/confirm`.
При запросах браузер отправляет cookies автоматически.

### Регистрация и вход

1. **POST /v1/auth/register** — email, пароль → на почту уходит 6-значный код
2. **POST /v1/auth/register/confirm** — jti + code → cookies + success
3. **POST /v1/auth/login** — email, пароль → на почту уходит код
4. **POST /v1/auth/login/confirm** — jti + code → cookies + success
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Проверка JWT-ключей при старте — падаем сразу с понятной ошибкой, а не при первом запросе.
    try:
        _get_jwt_private_key()
        _get_jwt_public_key()
    except RuntimeError as e:
        logger.error("JWT keys validation failed: %s", e)
        raise
    yield
    await close_redis()


app = FastAPI(
    title="JurBot API",
    description=OPENAPI_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: для фронта на другом origin задайте CORS_ORIGINS в .env (через запятую, например http://localhost:3000).
_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(router)


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc   
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)