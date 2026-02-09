"""Точка входа AI Chat микросервиса."""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router
from app.core import init_mongodb, close_mongodb


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongodb()
    yield
    await close_mongodb()


app = FastAPI(
    title="AI Chat Service",
    description="Эхо-чат с сохранением в MongoDB. Вызывается через JurBot backend.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router, prefix="/ai_chat")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
