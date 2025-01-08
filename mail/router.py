from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from mail import service as mail_service
from auth import service as auth_service

mail_router = APIRouter(tags=['mail'])

@mail_router.post('/get_activation_code', description='Отправить код активации пользователя')
async def get_activation_code(
    background_tasks: BackgroundTasks,
    token: str = Depends(auth_service.oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    user = await auth_service.get_current_user(token=token, session=session)
    return await mail_service.send_activation_code(
        email=user.email, 
        session=session, 
        background_tasks=background_tasks
    )

@mail_router.post('/get_reset_code', description='Отправить код восстановления пароля')
async def get_reset_code(
    email: str, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    
):
    return await mail_service.send_reset_password_code(
        email=email, 
        session=session,
        background_tasks=background_tasks
    )