"""Эндпоинты аутентификации: регистрация, вход, подтверждение по коду из email."""
import jwt
from fastapi import APIRouter, Depends, Request, Response

from app.core.logging import get_logger
from app.core.rate_limit import limiter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session
from app.core.dependencies import get_company_repo, get_user_repo
from app.core.security import (
    ACCESS_TOKEN_COOKIE_MAX_AGE,
    REFRESH_TOKEN_COOKIE_MAX_AGE,
    clear_token,
    decode_token,
    set_token,
)
from app.repository import CompanyRepository, UserRepository
from app.schemas import Confirm, Login, UserCreate
from app.services import AuthService

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Регистрация (шаг 1)",
    description="Отправляет 6-значный код на email. Код действует 15 минут. Используйте его в `/register/confirm`.",
    response_model=dict,
    responses={
        200: {"description": "Код отправлен на email", "content": {"application/json": {"example": {"jti": "550e8400-e29b-41d4-a716-446655440000"}}}},
        400: {"description": "Пользователь уже существует"},
        429: {"description": "Превышен лимит запросов (10/мин)"},
    },
)
@limiter.limit("10/minute")
async def register(
    request: Request,
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    jti = await AuthService.register(session, redis, user_repo, user)
    return {"jti": str(jti)}


@router.post(
    "/register/confirm",
    summary="Подтверждение регистрации (шаг 2)",
    description="Принимает jti из `/register` и код из email. Устанавливает access_token и refresh_token в httponly cookies.",
    response_model=dict,
    responses={
        200: {"description": "Успешная регистрация", "content": {"application/json": {"example": {"status": "success"}}}},
        401: {"description": "Неверный или истёкший код"},
    },
)
async def confirm_register(
    response: Response,
    data: Confirm,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    access_token, refresh_token = await AuthService.confirm_registration(session, redis, user_repo, data)
    set_token(response, access_token, "access_token", ACCESS_TOKEN_COOKIE_MAX_AGE)
    set_token(response, refresh_token, "refresh_token", REFRESH_TOKEN_COOKIE_MAX_AGE)
    return {"status": "success"}


@router.post(
    "/login",
    summary="Вход (шаг 1)",
    description="Проверяет email и пароль, отправляет 6-значный код на email. Используйте его в `/login/confirm`.",
    response_model=dict,
    responses={
        200: {"description": "Код отправлен на email", "content": {"application/json": {"example": {"jti": "550e8400-e29b-41d4-a716-446655440000"}}}},
        401: {"description": "Неверный email или пароль"},
        429: {"description": "Превышен лимит запросов (10/мин)"},
    },
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: Login,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    jti = await AuthService.login(session, redis, user_repo, data)
    return {"jti": str(jti)}


@router.post(
    "/login/confirm",
    summary="Подтверждение входа (шаг 2)",
    description="Принимает jti из `/login` и код из email. Устанавливает cookies. Возвращает status: 'success' или 'you do not have a company yet'.",
    response_model=dict,
    responses={
        200: {"description": "Успешный вход", "content": {"application/json": {"examples": {"with_company": {"value": {"status": "success"}}, "no_company": {"value": {"status": "you do not have a company yet"}}}}}},
        401: {"description": "Неверный или истёкший код"},
    },
)
async def confirm_login(
    response: Response,
    data: Confirm,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    access_token, refresh_token, message = await AuthService.confirm_login(session, redis, company_repo, data)
    set_token(response, access_token, "access_token", ACCESS_TOKEN_COOKIE_MAX_AGE)
    set_token(response, refresh_token, "refresh_token", REFRESH_TOKEN_COOKIE_MAX_AGE)
    return {"status": message}


@router.post(
    "/logout",
    summary="Выход",
    description="Очищает cookies (access_token, refresh_token) и при наличии refresh_token — инвалидирует его в Redis.",
    response_model=dict,
    responses={200: {"description": "Успешный выход"}},
)
async def logout(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            if user_id:
                await redis.delete(f"{user_id}_refresh_token")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
        except Exception as e:
            logger.warning("Logout: unexpected error invalidating refresh token: %s", e)
    clear_token(response, "access_token")
    clear_token(response, "refresh_token")
    return {"status": "logged out"}
