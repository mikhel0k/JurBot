from .api.router import router as api_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(api_router)
