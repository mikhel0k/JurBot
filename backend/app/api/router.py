from fastapi import APIRouter

from app.api.v1.Auth import router as AuthRouter
from app.api.v1.Company import router as CompanyRouter
from app.api.v1.Employee import router as EmployeeRouter


router = APIRouter(prefix="/v1")
router.include_router(AuthRouter)
router.include_router(CompanyRouter)
router.include_router(EmployeeRouter)