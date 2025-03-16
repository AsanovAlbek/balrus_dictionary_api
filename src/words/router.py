from fastapi import APIRouter, Response, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from words import schema
from words import service
from database.database import get_async_session


dictionary_router = APIRouter(tags=['dictionary'])

@dictionary_router.post('/add_word', description='Добавить слово')
async def add_word(word: schema.Word, session: AsyncSession=Depends(get_async_session)):
    return await service.add_word(word, session)

@dictionary_router.post('/update_word', description='Обновить слово')
async def update_word(word: schema.Word, session: AsyncSession=Depends(get_async_session)):
    return await service.update_word(word, session)

@dictionary_router.delete('/remove_word/{word_id}', description='Удалить слово')
async def remove_word(word_id: int, session: AsyncSession=Depends(get_async_session)):
    return await service.delete_word(word_id, session)

@dictionary_router.get('/get_words', description='Получить слова по названию')
async def get_words(
    name: str='',
    page: int=0,
    size: int=100,
    session: AsyncSession=Depends(get_async_session)
):
    return await service.get_words(name, page, size, session)

@dictionary_router.get('/words_count', description='Количество слов по названию')
async def words_count(name: str='', session: AsyncSession=Depends(get_async_session)):
    return await service.words_count(name, session)


@dictionary_router.get('/word_by_id', description='Слово по ID')
async def word_by_id(id: int, session: AsyncSession=Depends(get_async_session)):
    return await service.word_by_id(id, session)
