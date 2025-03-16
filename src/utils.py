from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

def handle_internal_error(exception: Exception):
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
        detail=f"Ошибка сервера {exception}")

async def try_commit(
        session: AsyncSession, 
        on_error: Callable[[Exception], None] = None) -> bool:
    try:
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        print(e)
        if on_error:
            on_error(e)
        return False
    
