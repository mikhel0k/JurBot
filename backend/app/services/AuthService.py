import json
from fastapi import HTTPException, status
from app.schemas import UserCreate, UserResponse
from app.repository import UserRepository
from app.models.User import User
from app.core import get_password_hash, create_token
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from uuid import uuid4
from random import randint
from app.core import send_code_email_gmail


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
    send_code_email_gmail(user_data["email"], code)
    await redis.set(user_data["email"], "registering", ex=60*15)
    await redis.set(user_data["phone_number"], "registering", ex=60*15)
    await redis.set(f"{reg_id}_{code}", json.dumps(user_data), ex=60*15)
    return reg_id

async def confirm_registration(session: AsyncSession, redis: Redis, reg_id: uuid4, code: str):
    data = await redis.get(f"{reg_id}_{code}")
    if data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
    user_data = json.loads(data)
    await redis.delete(f"{reg_id}_{code}")
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
    
