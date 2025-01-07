from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_async_session
from media import service
from media import media_utils

media_router = APIRouter(tags=['media'])

@media_router.post('/upload_file')
async def upload_file(file: UploadFile):

    async def upload(sftp, ssh):
        return await service.upload_file(sftp=sftp, upload_file=file)
    
    return await media_utils.try_connect(
        config=service.config,
        on_success=upload
    )

@media_router.post('/delete_file')
async def delete_file(file_path: str):
    async def delete(sftp, ssh):
        return await service.delete_file(sftp=sftp, file_path=file_path)
    
    return await media_utils.try_connect(
        config=service.config,
        on_success=delete
    )

@media_router.get('/get_file')
async def get_file(file_path: str):
    async def get(sftp, ssh):
        return await service.get_file(sftp=sftp, file_path=file_path)
    return await media_utils.try_connect(
        config=service.config,
        on_success=get
    )

@media_router.get('/files_list')
async def files_list():
    async def rfiles(sftp, ssh):
        return await service.files_list(sftp=sftp)
    return await media_utils.try_connect(
        config=service.config,
        on_success=rfiles
    )