from fastapi import APIRouter, Depends

from app.core.dependencies import get_company_id
from app.services import EmployeeService
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.core import get_session, get_redis
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
router = APIRouter(prefix="/employee", tags=["employee"])


@router.post("/")
async def create_employee(
    employee: EmployeeCreate, 
    company_id: int=Depends(get_company_id),
    session: AsyncSession=Depends(get_session),
    redis: Redis=Depends(get_redis)
    ):
    employee = await EmployeeService.create_employee(session, redis, employee, company_id)
    return employee


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int, 
    company_id: int=Depends(get_company_id), 
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis)
    ):
    employee = await EmployeeService.get_employee(session, redis, employee_id, company_id)
    return employee


@router.patch("/{employee_id}")
async def update_employee(
    employee_id: int, 
    employee_data: EmployeeUpdate, 
    company_id: int=Depends(get_company_id), 
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis)):
    employee = await EmployeeService.update_employee(session, redis, employee_id, employee_data, company_id)
    return employee


@router.delete("/")
async def dismiss_employees(
    employee_ids: list[int], 
    company_id: int=Depends(get_company_id), 
    session: AsyncSession=Depends(get_session), 
    redis: Redis=Depends(get_redis)):
    return await EmployeeService.dismiss_employees(session, redis, employee_ids, company_id)
