import paramiko.config
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, File, status, HTTPException
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
import paramiko
from typing import Callable
from media import media_utils, file_validator
from media.model import SFTPConfig
import logging
import base64
from starlette.responses import JSONResponse

SFTP_HOSTNAME = getenv("SFTP_HOSTNAME")
SFTP_PORT = getenv("SFTP_PORT")
SFTP_USERNAME = getenv("SFTP_USERNAME")
SFTP_PASSWORD = getenv("SFTP_PASSWORD")
AUDIO_FOLDER_URL = getenv("AUDIO_FOLDER_URL")
FOLDER_URL = getenv("FOLDER_URL")
STATIC_FOLDER = getenv("STATIC_FOLDER")

config = SFTPConfig(
    host=SFTP_HOSTNAME,
    port=int(SFTP_PORT),
    username=SFTP_USERNAME,
    password=SFTP_PASSWORD
)


async def upload_file(
    sftp: paramiko.SFTPClient,
    upload_file: UploadFile
):
    validator = file_validator.FileValidator(file=upload_file)
    if not validator.validate_size():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Размер файла не должен превышать {validator.max_size_mb} мб"
        )
    if not validator.vaildate_type():
        available_types = ', '.join(validator.audio_extensions)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неправильный тип файла. Допустимые типы: {available_types}"
        )
    file_path = await media_utils.create_unique_filepath(upload_file, FOLDER_URL)
    sftp.putfo(upload_file.file, file_path)
    filename = file_path.split('/')[-1]
    file_url = STATIC_FOLDER + filename
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {upload_file.filename} успешно добавлен",
            "file_path": file_path,
            "file_url": file_url
        }
    )


async def delete_file(
    file_path: str,
    sftp: paramiko.SFTPClient,
):
    sftp.remove(file_path)
    removed_file_name = file_path.split('/')[-1]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {removed_file_name} успешно удален",
            "file_path": file_path
        }
    )


async def get_file(file_path: str, sftp: paramiko.SFTPClient):
    with sftp.open(file_path, "rb") as remote_file:
        audio_bytes = remote_file.read()
        contents = base64.b64encode(audio_bytes).decode()
    remote_file_name = file_path.split('/')[-1]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {remote_file_name} получен успешно",
            "file_bytes": contents
        }
    )


async def files_list(sftp: paramiko.SFTPClient):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Список всех файлов",
            "files": sftp.listdir(FOLDER_URL)
        }
    )
