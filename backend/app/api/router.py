from fastapi import APIRouter

from app.api.v1.Auth import router as AuthRouter


router = APIRouter(prefix="/v1")
router.include_router(AuthRouter)