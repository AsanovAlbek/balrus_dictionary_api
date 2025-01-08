from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from suggestion import schema
from database.database import get_async_session
from suggestion import service
from auth.router import oauth2_scheme, get_current_user

suggests_router = APIRouter(tags=['suggests'])

@suggests_router.post('/suggest_word', description='Предложить слово')
async def suggest_word(
    suggest: schema.CreateSuggestWord, 
    session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme)
):
    user = await get_current_user(token=token, session=session)
    return await service.suggest(
        suggest_word=suggest, 
        session=session,
        user_id = user.id
    )

@suggests_router.get('/get_suggest_words', description='Предложенные слова по названию')
async def get_suggest_words(
    token: str = Depends(oauth2_scheme),
    name: str = '', 
    page: int = 0, 
    size: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    user = await get_current_user(token=token, session=session)
    return await service.get_suggests(
        user_id=user.id, 
        name=name, 
        page=page, 
        size=size, 
        session=session
    )

@suggests_router.get('/all_suggest_words', description='Все предложенные слова по названию')
async def get_all_suggest_words(
    name: str = '', 
    page: int = 0, 
    size: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    return await service.get_all_suggests(
        name=name, 
        page=page, 
        size=size, 
        session=session
    )

@suggests_router.get('/suggests_count', description='Количество предложенных слов по названию')
async def suggests_count(
    name: str = '', 
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_async_session)
):
    user = await get_current_user(token=token, session=session)
    return await service.suggests_size(name=name, user_id=user.id, session=session)

@suggests_router.get('/all_suggests_count', description='Количество всех предложенных слов')
async def all_suggests_count(
    name: str = '', 
    session: AsyncSession = Depends(get_async_session)
):
    return await service.all_suggests_size(name=name, session=session)


@suggests_router.post('/accept_suggest', description='Принять слово')
async def accept_suggest(suggest_id: int, session: AsyncSession = Depends(get_async_session)):
    return service.accept(suggest_id, session)

@suggests_router.post('/reject_suggest', description='Отклонить слово')
async def reject_suggest(suggest_id: int, session: AsyncSession = Depends(get_async_session)):
    return await service.reject(suggest_id, session)
