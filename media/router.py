from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
import service
import media_utils

media_router = APIRouter(tags=['media'])

@media_router.post('/upload_file')
async def upload_file(file: UploadFile):
    return media_utils.try_connect(
        config=service.config,
        on_success=lambda sftp, _: service.upload_file(sftp=sftp, upload_file=file)
    )

@media_router.post('/delete_file')
async def delete_file(file_path: str, session: AsyncSession = Depends(get_async_session)):
    return media_utils.try_connect(
        config=service.config,
        on_success=lambda sftp, _: service.delete_file(sftp=sftp, file_path=file_path)
    )

@media_router.get('/get_file')
async def get_file(file_path: str):
    return media_utils.try_connect(
        config=service.config,
        on_success=lambda sftp, _: service.get_file(sftp=sftp, file_path=file_path)
    )

@media_router.get('/files_list')
async def files_list():
    return media_utils.try_connect(
        config=service.config,
        on_success=lambda sftp, _: service.files_list(sftp=sftp)
    )