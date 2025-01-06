from database.database import get_async_session
import schema
from fastapi import status, HTTPException, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import model
from typing import Optional
import utils


async def word_by_id(id: int, session: AsyncSession) -> model.Word:
    result = await session.execute(select(model.Word).filter_by(id=id))
    word = result.scalars().first()
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Слово с id {id} не найдено"
        )
    return word


async def add_word(word: schema.Word, session: AsyncSession) -> bool:
    db_word = model.Word(
        name=word.name,
        meaning=word.meaning,
        audio_url=word.audio_url
    )
    session.add(db_word)
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Слово добавлено успешно",
            "word": db_word
        }
    )


async def update_word(word: schema.Word, session: AsyncSession):
    db_word = await word_by_id(id=word.id, session=session)
    db_word.name = word.name
    db_word.meaning = word.meaning
    db_word.audio_url = word.audio_url
    session.add(db_word)
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Слово успешно обновлено",
            "word": db_word
        }
    )


async def delete_word(word_id: int, session: AsyncSession):
    db_word = await word_by_id(id=word_id, session=session)
    session.delete(db_word)
    utils.try_commit(session, on_error=utils.handle_internal_error)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Слово успешно удалено",
            "word": db_word
        }
    )


async def get_words(
    name: str,
    page: int,
    size: int,
    session: AsyncSession
):
    skip = page * size
    result = await session.execute(
        select(model.Word)
        .filter(model.Word.name.like(f'{name}%'))
        .order_by(model.Word.name)
        .offset(skip)
        .limit(size)
    )
    return result.scalars().all()


async def words_count(name: str, session: AsyncSession):
    result = await session.execute(
        select(func.count())
        .filter(model.Word.name.ilike(f'{name}%'))
    )
    return result.scalar()
