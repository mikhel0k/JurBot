from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.User import User
from app.repository.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(User)
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_phone_number(self, session: AsyncSession, phone_number: str) -> Optional[User]:
        query = select(User).where(User.phone_number == phone_number)
        result = await session.execute(query)
        return result.scalar_one_or_none()
