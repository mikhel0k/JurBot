
from fastapi import HTTPException, Request

from app.core.security import decode_token
from app.repository import CompanyRepository, EmployeeRepository, UserRepository

async def get_user_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = decode_token(token)
    try:
        return int(payload["sub"])
    except KeyError:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_company_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    payload = decode_token(token)
    try:
        company_id = payload["company_id"]
    except KeyError:
        raise HTTPException(status_code=401, detail="You do not have a company yet")
    if company_id is None:
        raise HTTPException(status_code=401, detail="You do not have a company yet")
    return int(company_id)


def get_employee_repo() -> EmployeeRepository:
    return EmployeeRepository()


def get_company_repo() -> CompanyRepository:
    return CompanyRepository()


def get_user_repo() -> UserRepository:
    return UserRepository()
