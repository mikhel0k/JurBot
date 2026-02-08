import json
import logging

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import create_token, get_logger
from app.models.Company import Company
from app.repository import CompanyRepository
from app.schemas import CompanyCreate, CompanyResponse, CompanyUpdate

logger = get_logger(__name__)


async def create_company(session: AsyncSession, redis: Redis, company_data: CompanyCreate, user_id: int):
    logger.info("Creating company for user_id=%s", user_id)
    try:
        if await CompanyRepository().get_by_user_id(session, user_id):
            logger.warning("Company already exists for user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists")
        company = company_data.model_dump()
        company["owner_id"] = user_id
        company_in_db = await CompanyRepository().create(session, Company(**company))
        result = CompanyResponse.model_validate(company_in_db)
        await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
        await session.commit()
        data_for_token = {"sub": str(user_id), "company_id": company_in_db.id}
        access_token = create_token(data_for_token)
        logger.info("Company created id=%s user_id=%s", company_in_db.id, user_id)
        return result, access_token
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create company: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def get_company(session: AsyncSession, redis: Redis, user_id: int):
    logger.debug("Getting company for user_id=%s", user_id)
    try:
        cached = await redis.get(f"company_{user_id}")
        if cached:
            logger.debug("Company from cache user_id=%s", user_id)
            return CompanyResponse.model_validate(json.loads(cached))
        company_in_db = await CompanyRepository().get_by_user_id(session, user_id)
        if not company_in_db:
            logger.warning("Company not found user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        result = CompanyResponse.model_validate(company_in_db)
        await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get company user_id=%s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def update_company(session: AsyncSession, redis: Redis, user_id: int, company_data: CompanyUpdate):
    logger.info("Updating company for user_id=%s", user_id)
    try:
        company_in_db = await CompanyRepository().get_by_user_id(session, user_id)
        if not company_in_db:
            logger.warning("Company not found user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        for key, value in company_data.model_dump(exclude_none=True).items():
            setattr(company_in_db, key, value)
        company_in_db = await CompanyRepository().update(session, company_in_db)
        result = CompanyResponse.model_validate(company_in_db)
        if await redis.get(f"company_{user_id}"):
            await redis.delete(f"company_{user_id}")
        await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
        await session.commit()
        logger.info("Company updated id=%s user_id=%s", company_in_db.id, user_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update company user_id=%s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
