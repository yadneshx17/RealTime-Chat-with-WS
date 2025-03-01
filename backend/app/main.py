from fastapi import FastAPI, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from .models import models
from .db.db import get_async_db, engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    lifespan=lifespan
    )


@app.get("/")
async def root(db: AsyncSession = Depends(get_async_db)):
    return {"message": " Hello"}