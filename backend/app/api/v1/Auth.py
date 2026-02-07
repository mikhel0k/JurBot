from fastapi import APIRouter, Response
from app.core import get_session, get_redis
from app.schemas import UserCreate, Confirm_Registration, Login
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from fastapi import Depends

from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user: UserCreate, 
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis)
    ):
    jti = await AuthService.register(session, redis, user)
    return {
        "jti": jti,
    }

@router.post("/register/confirm")
async def confirm_register(
    response: Response,
    data: Confirm_Registration,
    session: AsyncSession=Depends(get_session),
    redis: Redis=Depends(get_redis)
):
    access_token, refresh_token = await AuthService.confirm_registration(session, redis, data.jti, data.code)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=True,
        max_age=60*30,
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=True,
        max_age=60*60*24*30,
        path="/",
    )
    return {
        "status": "success",
    }