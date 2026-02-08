"""Эндпоинты управления компанией. Требуют аутентификации (cookies)."""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session, get_user_id
from app.core.dependencies import get_company_repo
from app.core.security import ACCESS_TOKEN_COOKIE_MAX_AGE, set_token
from app.repository import CompanyRepository
from app.schemas import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services import CompanyService

router = APIRouter(prefix="/company", tags=["company"])


@router.post(
    "/",
    summary="Создать компанию",
    description="Создаёт компанию для текущего пользователя. Требует access_token в cookie. Обновляет access_token с company_id.",
    response_model=CompanyResponse,
    responses={
        200: {"description": "Компания создана"},
        400: {"description": "У пользователя уже есть компания"},
        401: {"description": "Не авторизован (нет cookies или истёк токен)"},
    },
)
async def create_company(
    response: Response,
    company: CompanyCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    result, access_token = await CompanyService.create_company(session, redis, company_repo, company, user_id)
    set_token(response, access_token, "access_token", ACCESS_TOKEN_COOKIE_MAX_AGE)
    return result


@router.get(
    "/",
    summary="Получить свою компанию",
    description="Возвращает компанию текущего пользователя. Сначала ищет в Redis, при промахе — в БД.",
    response_model=CompanyResponse,
    responses={
        200: {"description": "Компания найдена"},
        404: {"description": "Компания не найдена"},
        401: {"description": "Не авторизован"},
    },
)
async def get_company(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    return await CompanyService.get_company(session, redis, company_repo, user_id)


@router.patch(
    "/",
    summary="Обновить компанию",
    description="Частичное обновление полей компании. Передавайте только изменяемые поля.",
    response_model=CompanyResponse,
    responses={
        200: {"description": "Компания обновлена"},
        404: {"description": "Компания не найдена"},
        401: {"description": "Не авторизован"},
    },
)
async def update_company(
    company: CompanyUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    return await CompanyService.update_company(session, redis, company_repo, user_id, company)
    