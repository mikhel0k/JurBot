from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Employee import Employee
from app.repository.BaseRepository import BaseRepository


class EmployeeRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Employee)

    async def get_all_by_company_id(self, session: AsyncSession, company_id: int) -> list[Employee]:
        result = await session.execute(select(Employee).where(Employee.company_id == company_id))
        return list(result.scalars().all())
        