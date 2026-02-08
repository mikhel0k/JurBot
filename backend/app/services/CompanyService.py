import json
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Company import Company
from app.schemas import CompanyCreate, CompanyResponse, CompanyUpdate
from app.repository import CompanyRepository
from fastapi import HTTPException, status


async def create_company(session: AsyncSession, redis: Redis, company_data: CompanyCreate, user_id: int):
    if await CompanyRepository().get_by_user_id(session, user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists")
    company = company_data.model_dump()
    company["owner_id"] = user_id
    company_in_db = await CompanyRepository().create(session, Company(**company))
    company = CompanyResponse.model_validate(company_in_db)
    await redis.set(f"company_{user_id}", json.dumps(company.model_dump()), ex=60*30)
    await session.commit()
    return company


async def get_company(session: AsyncSession, redis: Redis, user_id: int):
    company = await redis.get(f"company_{user_id}")
    if company:
        return CompanyResponse.model_validate(json.loads(company))
    company_in_db = await CompanyRepository().get_by_user_id(session, user_id)
    if company_in_db:
        company = CompanyResponse.model_validate(company_in_db)
        await redis.set(f"company_{user_id}", json.dumps(company.model_dump()), ex=60*30)
        return company
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")


async def update_company(session: AsyncSession, redis: Redis, user_id: int, company_data: CompanyUpdate):
    company_in_db_old = await CompanyRepository().get_by_user_id(session, user_id)
    if company_in_db_old: 
        for key, value in company_data.model_dump(exclude_none=True).items():
            setattr(company_in_db_old, key, value)
        company_in_db = await CompanyRepository().update(session, company_in_db_old)
        company = CompanyResponse.model_validate(company_in_db)
        if await redis.get(f"company_{user_id}"):
            await redis.delete(f"company_{user_id}")
        await redis.set(f"company_{user_id}", json.dumps(company.model_dump()), ex=60*30)
        await session.commit()
        return company
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
