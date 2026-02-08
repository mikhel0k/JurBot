from fastapi import APIRouter, Depends
from fastapi.responses import Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session, get_user_id
from app.core.dependencies import get_company_repo
from app.repository import CompanyRepository
from app.schemas import CompanyCreate, CompanyUpdate
from app.services import CompanyService

router = APIRouter(prefix="/company", tags=["company"])


@router.post("/")
async def create_company(
    response: Response,
    company: CompanyCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    result, access_token = await CompanyService.create_company(session, redis, company_repo, company, user_id)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, max_age=60 * 60 * 24 * 30)
    return result


@router.get("/")
async def get_company(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    return await CompanyService.get_company(session, redis, company_repo, user_id)


@router.patch("/")
async def update_company(
    company: CompanyUpdate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_id: int = Depends(get_user_id),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    return await CompanyService.update_company(session, redis, company_repo, user_id, company)
    