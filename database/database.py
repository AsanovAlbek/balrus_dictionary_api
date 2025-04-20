from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import database.config as config
from typing import AsyncGenerator

engine = create_async_engine(config.DATABASE_URL)
async_sessionmaker = async_sessionmaker(expire_on_commit=False, bind=engine)

class Base(DeclarativeBase):
    ...

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker() as session:
        yield session