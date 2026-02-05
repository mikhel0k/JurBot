import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import router
from app.core.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)