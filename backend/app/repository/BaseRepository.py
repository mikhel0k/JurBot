from typing import Type, TypeVar, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository:
    def __init__(self, model: Type[ModelT]):
        self._model = model

    async def get_by_id(self, session: AsyncSession, id: int) -> Optional[ModelT]:
        return await session.get(self._model, id)

    async def get_all(self, session: AsyncSession) -> list[ModelT]:
        result = await session.execute(select(self._model))
        return result.scalars().all()

    async def create(self, session: AsyncSession, data: ModelT) -> ModelT:
        session.add(data)
        await session.flush()
        await session.refresh(data)
        return data
    
    async def update(self, session: AsyncSession, data: ModelT) -> ModelT:
        session.add(data)
        await session.flush()
        await session.refresh(data)
        return data
    
    async def delete(self, session: AsyncSession, id: int) -> None:
        await session.delete(await self.get_by_id(session, id))
        await session.flush()
