import json
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from uuid import uuid4
from random import randint
import asyncio

from app.core import send_code_email_gmail
from app.schemas import Confirm, UserCreate, UserResponse, Login
from app.repository import UserRepository
from app.models.User import User
from app.core import get_password_hash, create_token, verify_password
from app.repository import CompanyRepository
from app.schemas import CompanyResponse


async def register(session: AsyncSession, redis: Redis, user: UserCreate):
    if await redis.exists(user.email) or await redis.exists(user.phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    if await UserRepository().get_by_email(session, user.email) or await UserRepository().get_by_phone_number(session, user.phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user_data = user.model_dump()
    user_data["password_hash"] = get_password_hash(user_data["password"])
    user_data.pop("password")
    code = ""
    reg_id = uuid4()
    for _ in range(6):
        code += str(randint(0, 9))
    await asyncio.to_thread(send_code_email_gmail, user_data["email"], code)
    await redis.set(user_data["email"], "registering", ex=60*15)
    await redis.set(user_data["phone_number"], "registering", ex=60*15)
    await redis.set(f"{reg_id}_{code}", json.dumps(user_data), ex=60*15)
    return reg_id


async def confirm_registration(session: AsyncSession, redis: Redis, data: Confirm):
    jti, code = data.jti, data.code
    payload = await redis.get(f"{jti}_{code}")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
    user_data = json.loads(payload)
    await redis.delete(f"{jti}_{code}")
    await redis.delete(user_data["email"])
    await redis.delete(user_data["phone_number"])
    user_instance = User(**user_data)
    user_in_db = await UserRepository().create(session, user_instance)
    user = UserResponse.model_validate(user_in_db)
    data_for_token = {
        "sub": user.id,
    }
    data_for_refresh_token = {
        "sub": user.id,
    }
    access_token = create_token(data_for_token)
    refresh_token = create_token(data_for_refresh_token)
    await session.commit()
    return access_token, refresh_token


async def login(session: AsyncSession, redis: Redis, data: Login):
    user_in_db = await UserRepository().get_by_email(session, data.email)
    if user_in_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not verify_password(data.password, user_in_db.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    user_data = UserResponse.model_validate(user_in_db).model_dump()
    code = ""
    reg_id = uuid4()
    for _ in range(6):
        code += str(randint(0, 9))
    await asyncio.to_thread(send_code_email_gmail, user_data["email"], code)
    await redis.set(f"{reg_id}_{code}", json.dumps(user_data), ex=60*15)
    return reg_id


async def confirm_login(session: AsyncSession, redis: Redis, data: Confirm):
    jti, code = data.jti, data.code
    payload = await redis.get(f"{jti}_{code}")
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
    user_data = json.loads(payload)
    await redis.delete(f"{jti}_{code}")
    data_for_token = {
        "sub": user_data["id"],
    }
    data_for_refresh_token = {
        "sub": user_data["id"],
    }
    access_token = create_token(data_for_token)
    refresh_token = create_token(data_for_refresh_token)
    await redis.set(f"{user_data['id']}_refresh_token", refresh_token, ex=60*60*24*30)
    message = "you do not have a company yet"
    company_in_db = await CompanyRepository().get_by_user_id(session, user_data["id"])
    if company_in_db:
        await redis.set(f"company_{company_in_db.owner_id}", json.dumps(CompanyResponse.model_validate(company_in_db).model_dump()), ex=60*30)
        message = "success"
    return access_token, refresh_token, message
