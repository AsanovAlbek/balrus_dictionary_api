from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import schema
from database.database import get_async_session
import service

suggests_router = APIRouter(tags=['suggests'])

@suggests_router.post('/suggest_word', description='Предложить слово')
async def suggest_word(suggest: schema.SuggestWord, session: AsyncSession = Depends(get_async_session)):
    return service.suggest(suggest_word=suggest, session=session)

@suggests_router.get('/get_suggest_words', description='Предложенные слова по названию')
async def get_suggest_words(
    name: str = '', 
    user_id: int = None, 
    page: int = 0, 
    size: int = 100, 
    session: AsyncSession = Depends(get_async_session)
):
    return service.get_suggests(
        user_id=user_id, name=name, 
        page=page, 
        size=size, 
        session=session
    )

@suggests_router.get('/suggests_count', description='Количество предложенных слов по названию')
async def suggests_count(
    name: str = '', 
    user_id: int = None, 
    session: AsyncSession = Depends(get_async_session)
):
    return service.suggests_size(name=name, user_id=user_id, session=session)

@suggests_router.post('/accept_suggest', description='Принять слово')
async def accept_suggest(suggest_id: int, session: AsyncSession = Depends(get_async_session)):
    return service.accept(suggest_id, session)

@suggests_router.post('/reject_suggest', description='Отклонить слово')
async def reject_suggest(suggest_id: int, session: AsyncSession = Depends(get_async_session)):
    return service.reject(suggest_id, session)
