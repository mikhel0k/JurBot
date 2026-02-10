from fastapi import APIRouter

from app.api.v1 import auth, chat, company, employee

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(chat.router)
router.include_router(company.router)
router.include_router(employee.router)