"""Эндпоинты управления сотрудниками. Требуют аутентификации и наличие компании (cookies)."""
from fastapi import APIRouter, Body, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_redis, get_session
from app.core.dependencies import get_company_id, get_employee_repo
from app.repository import EmployeeRepository
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services import EmployeeService

router = APIRouter(prefix="/employee", tags=["employee"])


@router.get(
    "/",
    summary="Список сотрудников",
    description="Возвращает всех сотрудников компании текущего пользователя.",
    response_model=list[EmployeeResponse],
    responses={
        200: {"description": "Список сотрудников"},
        401: {"description": "Не авторизован или нет компании"},
    },
)
async def list_employees(
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.list_employees(session, employee_repo, company_id)


@router.post(
    "/",
    summary="Добавить сотрудника",
    description="Создаёт сотрудника в компании текущего пользователя. Требует access_token с company_id в cookie.",
    response_model=EmployeeResponse,
    responses={
        200: {"description": "Сотрудник создан"},
        401: {"description": "Не авторизован или у пользователя ещё нет компании"},
    },
)
async def create_employee(
    employee: EmployeeCreate,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.create_employee(session, redis, employee_repo, employee, company_id)


@router.get(
    "/{employee_id}",
    summary="Получить сотрудника",
    description="Возвращает сотрудника по id. Доступ только к сотрудникам своей компании.",
    response_model=EmployeeResponse,
    responses={
        200: {"description": "Сотрудник найден"},
        404: {"description": "Сотрудник не найден или принадлежит другой компании"},
        401: {"description": "Не авторизован или нет компании"},
    },
)
async def get_employee(
    employee_id: int,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.get_employee(session, redis, employee_repo, employee_id, company_id)


@router.patch(
    "/{employee_id}",
    summary="Обновить сотрудника",
    description="Частичное обновление данных сотрудника. Передавайте только изменяемые поля.",
    response_model=EmployeeResponse,
    responses={
        200: {"description": "Сотрудник обновлён"},
        404: {"description": "Сотрудник не найден или принадлежит другой компании"},
        401: {"description": "Не авторизован или нет компании"},
    },
)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.update_employee(session, redis, employee_repo, employee_id, employee_data, company_id)


@router.delete(
    "/",
    summary="Уволить сотрудников",
    description="Удаляет сотрудников по списку id. Все id должны относиться к компании текущего пользователя.",
    response_model=dict,
    responses={
        200: {"description": "Сотрудники уволены", "content": {"application/json": {"example": {"message": "Employees dismissed successfully"}}}},
        404: {"description": "Один из сотрудников не найден или принадлежит другой компании"},
        401: {"description": "Не авторизован или нет компании"},
    },
)
async def dismiss_employees(
    employee_ids: list[int] = Body(..., description="Список id сотрудников для увольнения"),
    company_id: int = Depends(get_company_id),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    employee_repo: EmployeeRepository = Depends(get_employee_repo),
):
    return await EmployeeService.dismiss_employees(session, redis, employee_repo, employee_ids, company_id)
