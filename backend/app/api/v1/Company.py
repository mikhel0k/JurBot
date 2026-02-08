from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from fastapi import Depends

from app.services import CompanyService
from app.core import get_session, get_redis
from app.schemas import CompanyCreate, CompanyUpdate
from app.core import get_user_id


router = APIRouter(prefix="/company", tags=["company"])


@router.post("/")
async def create_company(
    company: CompanyCreate, 
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis),
    user_id: int=Depends(get_user_id)
    ):
    return await CompanyService.create_company(session, redis, company, user_id)


@router.get("/")
async def get_company(
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis),
    user_id: int=Depends(get_user_id)
):
    return await CompanyService.get_company(session, redis, user_id)

@router.patch("/")
async def update_company(
    company: CompanyUpdate,
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis),
    user_id: int=Depends(get_user_id)
):
    return await CompanyService.update_company(session, redis, user_id, company)