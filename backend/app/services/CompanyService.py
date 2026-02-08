import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import create_token, get_logger
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models.Company import Company
from app.repository import CompanyRepository
from app.schemas import CompanyCreate, CompanyResponse, CompanyUpdate

logger = get_logger(__name__)


async def create_company(
    session: AsyncSession, redis: Redis, company_repo: CompanyRepository, company_data: CompanyCreate, user_id: int
):
    """Создаёт компанию для пользователя, кэширует в Redis, возвращает результат и access_token с company_id."""
    logger.info("Creating company for user_id=%s", user_id)
    if await company_repo.get_by_user_id(session, user_id):
        logger.warning("Company already exists for user_id=%s", user_id)
        raise AlreadyExistsError("Company already exists")
    company = company_data.model_dump()
    company["owner_id"] = user_id
    company_in_db = await company_repo.create(session, Company(**company))
    result = CompanyResponse.model_validate(company_in_db)
    await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
    await session.commit()
    data_for_token = {"sub": str(user_id), "company_id": company_in_db.id}
    access_token = create_token(data_for_token)
    logger.info("Company created id=%s user_id=%s", company_in_db.id, user_id)
    return result, access_token


async def get_company(
    session: AsyncSession, redis: Redis, company_repo: CompanyRepository, user_id: int
):
    """Возвращает компанию пользователя. Сначала проверяет кэш Redis, при промахе — БД."""
    logger.debug("Getting company for user_id=%s", user_id)
    cached = await redis.get(f"company_{user_id}")
    if cached:
        logger.debug("Company from cache user_id=%s", user_id)
        return CompanyResponse.model_validate(json.loads(cached))
    company_in_db = await company_repo.get_by_user_id(session, user_id)
    if not company_in_db:
        logger.warning("Company not found user_id=%s", user_id)
        raise NotFoundError("Company not found")
    result = CompanyResponse.model_validate(company_in_db)
    await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
    return result


async def update_company(
    session: AsyncSession, redis: Redis, company_repo: CompanyRepository, user_id: int, company_data: CompanyUpdate
):
    """Частично обновляет компанию, инвалидирует и обновляет кэш."""
    logger.info("Updating company for user_id=%s", user_id)
    company_in_db = await company_repo.get_by_user_id(session, user_id)
    if not company_in_db:
        logger.warning("Company not found user_id=%s", user_id)
        raise NotFoundError("Company not found")
    for key, value in company_data.model_dump(exclude_none=True).items():
        setattr(company_in_db, key, value)
    company_in_db = await company_repo.update(session, company_in_db)
    result = CompanyResponse.model_validate(company_in_db)
    if await redis.get(f"company_{user_id}"):
        await redis.delete(f"company_{user_id}")
    await redis.set(f"company_{user_id}", json.dumps(result.model_dump()), ex=60 * 30)
    await session.commit()
    logger.info("Company updated id=%s user_id=%s", company_in_db.id, user_id)
    return result
