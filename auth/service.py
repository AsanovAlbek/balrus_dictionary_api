from typing import Optional
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
import hashlib
import re
from sqlalchemy.ext.asyncio import AsyncSession
from auth import model, schema
from sqlalchemy import select
import random
import utils
from starlette.responses import JSONResponse

load_dotenv()
ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
ALGORITHM = os.getenv("ALGORITHM")
SALT = os.getenv('PASSWORD_SALT')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/jwt/login")


def create_token(data: dict, expire_delta: timedelta = timedelta(minutes=10)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str):
    return hashlib.sha512(password.encode() + SALT.encode()).hexdigest()


def check_password(password: str) -> bool:
    password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
    return bool(re.match(password_regex, password))


def check_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


async def create_user(user: schema.CreateUser, session: AsyncSession):
    if not check_email(user.email) or not check_password(user.password):
        raise HTTPException(
            status_code=400, detail="Неправильные логин или пароль")
    hashed_password = hash_password(user.password)

    new_user = model.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        imei=user.imei
    )

    session.add(new_user)
    return await utils.try_commit(session=session)


async def get_user_by_email(email: str, session: AsyncSession) -> Optional[model.User]:
    result = await session.execute(select(model.User).filter_by(email=email))
    return result.scalars().first()


async def get_user_by_id(user_id: int, session: AsyncSession) -> Optional[model.User]:
    result = await session.execute(select(model.User).filter_by(id=user_id))
    return result.scalars().first()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


async def authenticate_user(email: str, password: str, session: AsyncSession):
    user = await get_user_by_email(email=email, session=session)
    if not user and not verify_password(password, user.password):
        return None
    return user


async def login_user(email: str, password: str, session: AsyncSession):
    user = await authenticate_user(email=email, password=password, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильные логин или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_token(
        data={"id": user.id},
        expire_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token(
        data={"id": user.id},
        expire_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
    }

async def user_activation(code: str, user: schema.User, session: AsyncSession):
    activation = await session.execute(select(model.Activation).filter_by(user_email = user.email))
    res = activation.scalars().first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Не найден код активации"
        )
    
    if res.code != code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Неверный код активации"
        )
    
    if res.expiration_date < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Код активации устарел. Пожалуйста, запросите новый код активации"
        )
    
    db_user = await get_user_by_email(email=user.email, session=session)
    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт уже активирован"
        )
    db_user.is_active = True
    session.add(db_user)
    await utils.try_commit(session=session, on_error=utils.handle_internal_error)
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content={"message": "Аккаунт успешно активирован"}
    )
    


async def refresh_token(r_token: str):
    try:
        payload = jwt.decode(r_token, ACCESS_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            print('not user id')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate creditials")
        new_access_token = create_token(
            data={"id": user_id},
            expire_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return JSONResponse(content={"access_token": new_access_token, "token_type": "bearer"})
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f'jwt error {e}')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate creditials")


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = None):
    creditionals_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate creditionals",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise creditionals_exception
    except jwt.InvalidTokenError as jwte:
        raise creditionals_exception
    user = await get_user_by_id(user_id=user_id, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
    return schema.User(
        id=user.id,
        name=user.name,
        email=user.email,
        imei=user.imei
    )


def generate_code(digits_count: int = 6):
    return str(random.randint(10 ** digits_count, 10 ** (digits_count + 1) - 1))


async def create_reset_password_code(email: str, session: AsyncSession):
    user = await get_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"Пользователь с почтой {email} не найден")
    code = generate_code()
    check = await session.execute(select(model.Reset).filter_by(user_email=email))
    check = check.scalars().first()
    if check:
        t = datetime.now() - check.created_date
        if t.total_seconds() < timedelta(minutes=3).total_seconds():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Повторите запрос позднее"
            )
        await session.delete(check)
        await utils.try_commit(session=session)

    new_code = model.Reset(
        user_email=email,
        code=code,
        created_date=datetime.now(),
        expiration_date=datetime.now() + timedelta(minutes=10)
    )

    session.add(new_code)
    await utils.try_commit(session=session)
    return JSONResponse(content=code, status_code=status.HTTP_200_OK)


async def change_password(email: str, new_password: str, session: AsyncSession):
    if not check_password(new_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пароль должен состоять из минимум 8 символов, содержать заглавные и строчные латинские буквы и цифры")
    user = await get_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователь с почтой {email} не найден")
    user.password = hash_password(new_password)
    session.add(user)
    await utils.try_commit(session=session, on_error=utils.handle_internal_error)
    return JSONResponse(content="Пароль успешно изменён", status_code=status.HTTP_200_OK)
