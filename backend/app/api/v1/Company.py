from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from fastapi import Depends

from app.services import CompanyService
from app.core import get_session, get_redis
from app.schemas import CompanyCreate
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
