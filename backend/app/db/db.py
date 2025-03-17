# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ..core.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL) # echo=True : logs of table creationg in terminal
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession) 

class Base(DeclarativeBase):
    pass

# ✅ Dependency to get async DB session
async def get_async_db():
    async with async_session() as session:
        yield session  # Properly yielding session