import json
import logging

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_logger
from app.models.Employee import Employee
from app.repository import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate

logger = get_logger(__name__)

EMPLOYEE_NOT_FOUND = "Employee not found or you are not the owner of the company"


async def create_employee(
    session: AsyncSession, redis: Redis, employee_repo: EmployeeRepository, employee: EmployeeCreate, company_id: int
):
    logger.info("Creating employee for company_id=%s", company_id)
    try:
        employee_data = employee.model_dump()
        employee_data["company_id"] = company_id
        employee_instance = Employee(**employee_data)
        employee_in_db = await employee_repo.create(session, employee_instance)
        result = EmployeeResponse.model_validate(employee_in_db)
        await redis.set(f"employee_{result.id}", result.model_dump_json(), ex=60 * 30)
        await session.commit()
        logger.info("Employee created id=%s company_id=%s", result.id, company_id)
        return result
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.exception("Failed to create employee: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def get_employee(
    session: AsyncSession, redis: Redis, employee_repo: EmployeeRepository, employee_id: int, company_id: int
):
    logger.debug("Getting employee id=%s company_id=%s", employee_id, company_id)
    try:
        cached = await redis.get(f"employee_{employee_id}")
        if cached:
            data = json.loads(cached)
            if data.get("company_id") == company_id:
                logger.debug("Employee id=%s from cache", employee_id)
                return EmployeeResponse.model_validate(data)
        employee_in_db = await employee_repo.get_by_id(session, employee_id)
        if not employee_in_db or employee_in_db.company_id != company_id:
            logger.warning("Employee not found or access denied id=%s company_id=%s", employee_id, company_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EMPLOYEE_NOT_FOUND)
        result = EmployeeResponse.model_validate(employee_in_db)
        await redis.set(f"employee_{result.id}", result.model_dump_json(), ex=60 * 30)
        logger.debug("Employee id=%s from db, cached", employee_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get employee id=%s: %s", employee_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def update_employee(
    session: AsyncSession,
    redis: Redis,
    employee_repo: EmployeeRepository,
    employee_id: int,
    employee_data: EmployeeUpdate,
    company_id: int,
):
    logger.info("Updating employee id=%s company_id=%s", employee_id, company_id)
    try:
        employee_in_db = await employee_repo.get_by_id(session, employee_id)
        if not employee_in_db or employee_in_db.company_id != company_id:
            logger.warning("Employee not found or access denied id=%s company_id=%s", employee_id, company_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EMPLOYEE_NOT_FOUND)
        for key, value in employee_data.model_dump(exclude_none=True).items():
            setattr(employee_in_db, key, value)
        employee_in_db = await employee_repo.update(session, employee_in_db)
        result = EmployeeResponse.model_validate(employee_in_db)
        await redis.set(f"employee_{result.id}", result.model_dump_json(), ex=60 * 30)
        await session.commit()
        logger.info("Employee updated id=%s", employee_id)
        return result
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.exception("Failed to update employee id=%s: %s", employee_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


async def dismiss_employees(
    session: AsyncSession, redis: Redis, employee_repo: EmployeeRepository, employee_ids: list[int], company_id: int
):
    logger.info("Dismissing employees company_id=%s", company_id)
    try:
        for employee_id in employee_ids:
            employee_in_db = await employee_repo.get_by_id(session, employee_id)
            if not employee_in_db or employee_in_db.company_id != company_id:
                logger.warning("Employee not found or access denied id=%s company_id=%s", employee_id, company_id)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EMPLOYEE_NOT_FOUND)
            await employee_repo.delete(session, employee_in_db)
            await redis.delete(f"employee_{employee_id}")
            logger.info("Employee dismissed id=%s", employee_id)
        await session.commit()
        return {"message": "Employees dismissed successfully"}
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        logger.exception("Failed to dismiss employees: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")