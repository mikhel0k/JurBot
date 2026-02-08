import asyncio
import json
from random import randint
from uuid import uuid4

import jwt
from fastapi import HTTPException, status
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import (
    create_token,
    get_logger,
    get_password_hash,
    send_code_email_gmail,
    verify_password,
)
from app.core.security import decode_token, REFRESH_TOKEN_DURATION_MIN
from app.models.User import User
from app.repository import CompanyRepository, UserRepository
from app.schemas import CompanyResponse, Confirm, Login, LoginCachePayload, UserCreate, UserResponse

logger = get_logger(__name__)


async def register(session: AsyncSession, redis: Redis, user_repo: UserRepository, user: UserCreate):
    logger.info("Register attempt email=%s", user.email)
    try:
        if await redis.exists(user.email) or await redis.exists(user.phone_number):
            logger.warning("User already in redis email=%s", user.email)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        if await user_repo.get_by_email(session, user.email) or await user_repo.get_by_phone_number(
            session, user.phone_number
        ):
            logger.warning("User already in db email=%s", user.email)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        user_data = user.model_dump()
        user_data["password_hash"] = get_password_hash(user_data["password"])
        user_data.pop("password")
        code = "".join(str(randint(0, 9)) for _ in range(6))
        reg_id = uuid4()
        await asyncio.to_thread(send_code_email_gmail, user_data["email"], code)
        await redis.set(user_data["email"], "registering", ex=60 * 15)
        await redis.set(user_data["phone_number"], "registering", ex=60 * 15)
        await redis.set(f"{reg_id}_{code}", json.dumps(user_data), ex=60 * 15)
        logger.info("Register code sent jti=%s", reg_id)
        return reg_id
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to register: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def confirm_registration(session: AsyncSession, redis: Redis, user_repo: UserRepository, data: Confirm):
    logger.debug("Confirm registration jti=%s", data.jti)
    try:
        payload = await redis.get(f"{data.jti}_{data.code}")
        if payload is None:
            logger.warning("Invalid confirm code jti=%s", data.jti)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
        user_data = json.loads(payload)
        await redis.delete(f"{data.jti}_{data.code}")
        await redis.delete(user_data["email"])
        await redis.delete(user_data["phone_number"])
        user_instance = User(**user_data)
        user_in_db = await user_repo.create(session, user_instance)
        user = UserResponse.model_validate(user_in_db)
        access_token = create_token({"sub": str(user.id), "company_id": None})
        refresh_token = create_token({"sub": str(user.id)}, duration=REFRESH_TOKEN_DURATION_MIN)
        await session.commit()
        logger.info("User registered id=%s", user.id)
        return access_token, refresh_token
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.exception("Failed to confirm registration: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def login(session: AsyncSession, redis: Redis, user_repo: UserRepository, data: Login):
    logger.info("Login attempt email=%s", data.email)
    try:
        user_in_db = await user_repo.get_by_email(session, data.email)
        if user_in_db is None:
            logger.warning("Login failed user not found email=%s", data.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not verify_password(data.password, user_in_db.password_hash):
            logger.warning("Login failed wrong password email=%s", data.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        user_data = UserResponse.model_validate(user_in_db).model_dump()
        code = "".join(str(randint(0, 9)) for _ in range(6))
        reg_id = uuid4()
        await asyncio.to_thread(send_code_email_gmail, user_data["email"], code)
        await redis.set(f"{reg_id}_{code}", json.dumps(user_data), ex=60 * 15)
        logger.info("Login code sent jti=%s", reg_id)
        return reg_id
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to login: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def confirm_login(session: AsyncSession, redis: Redis, company_repo: CompanyRepository, data: Confirm):
    logger.debug("Confirm login jti=%s", data.jti)
    try:
        payload = await redis.get(f"{data.jti}_{data.code}")
        if payload is None:
            logger.warning("Invalid login code jti=%s", data.jti)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
        try:
            user_data = LoginCachePayload.model_validate(json.loads(payload))
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Invalid login cache payload jti=%s: %s", data.jti, e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
        await redis.delete(f"{data.jti}_{data.code}")
        company_in_db = await company_repo.get_by_user_id(session, user_data.id)
        access_token = create_token({
            "sub": str(user_data.id),
            "company_id": company_in_db.id if company_in_db else None,
        })
        refresh_token = create_token({"sub": str(user_data.id)}, duration=REFRESH_TOKEN_DURATION_MIN)
        await redis.set(f"{user_data.id}_refresh_token", refresh_token, ex=60 * 60 * 24 * 30)
        message = "you do not have a company yet"
        if company_in_db:
            await redis.set(
                f"company_{company_in_db.owner_id}",
                json.dumps(CompanyResponse.model_validate(company_in_db).model_dump()),
                ex=60 * 30,
            )
            message = "success"
        logger.info("User logged in id=%s company_id=%s", user_data.id, company_in_db.id if company_in_db else None)
        return access_token, refresh_token, message
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to confirm login: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def refresh_access_token(
    session: AsyncSession, company_repo: CompanyRepository, refresh_token: str
) -> str:
    """По валидному refresh-токену выдаёт новый access-токен. При невалидном/истёкшем — 401."""
    try:
        payload = decode_token(refresh_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        logger.warning("Refresh failed: invalid or expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError, TypeError):
        logger.warning("Refresh failed: invalid payload")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    company_in_db = await company_repo.get_by_user_id(session, user_id)
    company_id = company_in_db.id if company_in_db else None
    access_token = create_token({"sub": str(user_id), "company_id": company_id})
    logger.info("Access token refreshed for user_id=%s", user_id)
    return access_token
