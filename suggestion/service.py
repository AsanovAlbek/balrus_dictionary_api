from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from suggestion import model
from suggestion import schema
import utils
from sqlalchemy import select, func
from words.model import Word
from words import schema as words_schema
from starlette.responses import JSONResponse

async def suggest(
    suggest_word: schema.CreateSuggestWord, 
    session: AsyncSession,
    user_id: int
):
    db_suggest = model.SuggestWord(
        word = suggest_word.word,
        meaning = suggest_word.meaning,
        user_id = user_id
    )
    session.add(db_suggest)
    await utils.try_commit(session, on_error=utils.handle_internal_error)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Слово отправлено на рассмотрение",
            "suggest_word": schema.from_db(db_suggest).model_dump()
        }
    )

async def accept(suggest_id: int, session: AsyncSession):
    suggest = await get_suggest_by_id(suggest_id, session)
    word = Word(
        word = suggest.word,
        meaning = suggest.meaning,
        audio_url = '',
        audio_path = ''
    )
    session.add(word)
    await session.delete(suggest)
    # тут ещё можно отправлять пользователю сообщение, что его слово принято
    await utils.try_commit(session, on_error=utils.handle_internal_error)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Предложенное слово принято",
            "suggest": schema.from_db(suggest).model_dump(),
            "word": words_schema.from_db(word).model_dump()
        }
    )

async def reject(suggest_id: int, session: AsyncSession):
    suggest = await get_suggest_by_id(suggest_id, session)
    await session.delete(suggest)
    # тут ещё можно отправлять пользователю сообщение, что его слово отклонено
    await utils.try_commit(session, on_error=utils.handle_internal_error)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Предложенное слово отклонено",
            "suggest": schema.from_db(suggest).model_dump(),
            "word": None
        }
    )

async def get_suggest_by_id(id: int, session: AsyncSession):
    query = select(model.SuggestWord).filter_by(id=id)
    result = await session.execute(query)
    suggest = result.scalars().first()
    if not suggest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Слово не найдено")
    return suggest

async def get_suggests(
    user_id: int, 
    name: str, 
    page: int, 
    size: int, 
    session: AsyncSession
):
    query = select(model.SuggestWord).filter(model.SuggestWord.word.ilike(f'{name}%'))
    if user_id:
        query = query.filter_by(user_id=user_id)
    skip = page * size
    query = query.order_by(model.SuggestWord.word).offset(skip).limit(size)
    result = await session.execute(query)
    return result.scalars().all()

async def get_all_suggests(
    name: str, 
    page: int, 
    size: int, 
    session: AsyncSession
):
    query = select(model.SuggestWord).filter(model.SuggestWord.word.ilike(f'{name}%'))
    skip = page * size
    query = query.order_by(model.SuggestWord.word).offset(skip).limit(size)
    result = await session.execute(query)
    return result.scalars().all()

async def suggests_size(user_id: int, name: str, session: AsyncSession):
    query = select(func.count()).filter(model.SuggestWord.word.ilike(f'{name}%'))
    if user_id:
        query = query.filter(model.SuggestWord.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()

async def all_suggests_size(name: str, session: AsyncSession):
    query = select(func.count()).filter(model.SuggestWord.word.ilike(f'{name}%'))
    result = await session.execute(query)
    return result.scalar()