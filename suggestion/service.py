from fastapi import status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
import model
import schema
import utils
from sqlalchemy import select, func
from words.model import Word

async def suggest(suggest_word: schema.SuggestWord, session: AsyncSession):
    db_suggest = model.SuggestWord(
        id = suggest_word.id,
        word = suggest_word.word,
        meaning = suggest_word.meaning,
        user_id = suggest_word.user_id
    )
    session.add(db_suggest)
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Слово отправлено на рассмотрение",
            "suggest_word": db_suggest
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
    session.delete(suggest)
    # тут ещё можно отправлять пользователю сообщение, что его слово принято
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Предложенное слово принято",
            "suggest": suggest,
            "word": word
        }
    )

async def reject(suggest_id: int, session: AsyncSession):
    suggest = await get_suggest_by_id(suggest_id, session)
    session.delete(suggest)
    # тут ещё можно отправлять пользователю сообщение, что его слово отклонено
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Предложенное слово отклонено",
            "suggest": suggest,
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


async def suggests_size(user_id: int, name: str, session: AsyncSession):
    query = select(func.count()).filter(model.SuggestWord.word.ilike(f'{name}%'))
    if user_id:
        query = query.filter_by(user_id=user_id)
    result = await session.execute(query)
    return result.scalar()