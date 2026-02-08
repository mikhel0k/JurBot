from fastapi import APIRouter, Depends, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session
from app.core.dependencies import get_user_repo, get_company_repo
from app.repository import CompanyRepository, UserRepository
from app.schemas import Confirm, Login, UserCreate
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    jti = await AuthService.register(session, redis, user_repo, user)
    return {"jti": jti}


@router.post("/register/confirm")
async def confirm_register(
    response: Response,
    data: Confirm,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    access_token, refresh_token = await AuthService.confirm_registration(session, redis, user_repo, data)
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


@router.post("/login")
async def login(
    data: Login,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    user_repo: UserRepository = Depends(get_user_repo),
):
    jti = await AuthService.login(session, redis, user_repo, data)
    return {"jti": jti}


@router.post("/login/confirm")
async def confirm_login(
    response: Response,
    data: Confirm,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    access_token, refresh_token, message = await AuthService.confirm_login(session, redis, company_repo, data)
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
        "status": message,
    }
