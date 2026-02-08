import jwt
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import ACCESS_TOKEN_COOKIE_MAX_AGE, decode_token, set_token
from app.repository import CompanyRepository, EmployeeRepository, UserRepository
from app.services import AuthService


def get_employee_repo() -> EmployeeRepository:
    """Возвращает экземпляр EmployeeRepository. Используется как FastAPI Depends."""
    return EmployeeRepository()


def get_company_repo() -> CompanyRepository:
    """Возвращает экземпляр CompanyRepository. Используется как FastAPI Depends."""
    return CompanyRepository()


def get_user_repo() -> UserRepository:
    """Возвращает экземпляр UserRepository. Используется как FastAPI Depends."""
    return UserRepository()


def _decode_access_token(token: str) -> dict:
    try:
        return decode_token(token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="Unauthorized")


async def _get_validated_context(
    request: Request,
    response: Response,
    session: AsyncSession,
    company_repo: CompanyRepository,
) -> tuple[int, int | None]:
    """Проверяет access-токен; при отсутствии/истечении пробует refresh и выставляет новую access-куку. Возвращает (user_id, company_id)."""
    access_token = request.cookies.get("access_token")
    if access_token:
        try:
            payload = _decode_access_token(access_token)
            user_id = int(payload["sub"])
            company_id = payload.get("company_id")
            return user_id, int(company_id) if company_id is not None else None
        except HTTPException:
            pass
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        new_access = await AuthService.refresh_access_token(session, company_repo, refresh_token)
        set_token(response, new_access, "access_token", ACCESS_TOKEN_COOKIE_MAX_AGE)
        payload = decode_token(new_access)
        user_id = int(payload["sub"])
        company_id = payload.get("company_id")
        return user_id, int(company_id) if company_id is not None else None
    except HTTPException:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_user_id(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    user_id, _ = await _get_validated_context(request, response, session, company_repo)
    return user_id


async def get_company_id(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    company_repo: CompanyRepository = Depends(get_company_repo),
):
    _, company_id = await _get_validated_context(request, response, session, company_repo)
    if company_id is None:
        raise HTTPException(status_code=401, detail="You do not have a company yet")
    return company_id
