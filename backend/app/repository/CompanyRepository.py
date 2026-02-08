from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.Company import Company
from app.repository.BaseRepository import BaseRepository


class CompanyRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Company)
    
    async def get_by_user_id(self, session: AsyncSession, user_id: int) -> Company | None:
        result = await session.execute(select(Company).where(Company.owner_id == user_id))
        return result.scalar_one_or_none()
        