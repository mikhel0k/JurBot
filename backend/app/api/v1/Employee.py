from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session
from app.core.dependencies import get_company_id, get_employee_repo
from app.repository import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services import EmployeeService

router = APIRouter(prefix="/employee", tags=["employee"])


@router.post("/")
async def create_employee(
    employee: EmployeeCreate,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.create_employee(session, redis, employee_repo, employee, company_id)


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.get_employee(session, redis, employee_repo, employee_id, company_id)


@router.patch("/{employee_id}")
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.update_employee(session, redis, employee_repo, employee_id, employee_data, company_id)


@router.delete("/")
async def dismiss_employees(
    employee_ids: list[int],
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.dismiss_employees(session, redis, employee_repo, employee_ids, company_id)
