from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import service, schema
from database.database import get_async_session
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(tags=['auth'])
oauth2_scheme = OAuth2PasswordBearer()

@auth_router.post('/register', description='Регистрация')
async def register(user: schema.CreateUser, session: AsyncSession = Depends(get_async_session)):
    if await service.get_user_by_email(email=user.email, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Пользователь с такой почтой уже существует"
        )
    if not await service.create_user(user=user, session=session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    return schema.UserBase(
        name = user.name,
        email= user.email,
        imei= user.imei,
        is_active=user.is_active,
        is_admin=user.is_admin
    )

@auth_router.post('/login', description='Вход')
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    session: AsyncSession = Depends(get_async_session)
):
    return await service.login_user(
        email=form_data.username, 
        password=form_data.password, 
        session=session
    )

@auth_router.get('/current_user', description='Получить данные пользователя')
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_async_session)
):
    return await service.get_current_user()

@auth_router.post('/refresh_token', description='Обновить токен')
async def refresh_token(token: str):
    return await service.refresh_token(token)

@auth_router.post('/activate_user', description='Активация аккаунта')
async def activate_user(
    token: str = Depends(oauth2_scheme), 
    code: str = None, 
    session: AsyncSession = Depends(get_async_session)
):
    user = await get_current_user(token=token, session=session)
    return await service.user_activation(user=user, code=code, session=session)

@auth_router.post('/change_password', description='Сменить пароль')
async def change_password(
    new_password: str, 
    token: str = Depends(oauth2_scheme), 
    session: AsyncSession = Depends(get_async_session)
):
    user = await get_current_user(token=token, session=session)
    return await service.change_password(
        email=user.email, 
        new_password=new_password, 
        session=session
    )