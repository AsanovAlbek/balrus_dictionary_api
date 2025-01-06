import paramiko.config
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, File, status, HTTPException, Response
from dotenv import load_dotenv
from os import getenv
from datetime import datetime
import paramiko
from typing import Callable
import media_utils
from model import SFTPConfig
import logging
import base64

SFTP_HOSTNAME = getenv("SFTP_HOSTNAME")
SFTP_PORT = getenv("SFTP_PORT")
SFTP_USERNAME = getenv("SFTP_USERNAME")
SFTP_PASSWORD = getenv("SFTP_PASSWORD")
AUDIO_FOLDER_URL = getenv("AUDIO_FOLDER_URL")
FOLDER_URL = getenv("FOLDER_URL")
STATIC_FOLDER = getenv("STATIC_FOLDER")

config = SFTPConfig(
    hostname=SFTP_HOSTNAME,
    port=int(SFTP_PORT),
    username=SFTP_USERNAME,
    password=SFTP_PASSWORD
)


async def upload_file(
    sftp: paramiko.SFTPClient,
    upload_file: UploadFile
):
    file_path = media_utils.create_unique_filepath(upload_file, STATIC_FOLDER)
    sftp.putfo(file_path, upload_file.file)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {upload_file.filename} успешно добавлен",
            "file_path": file_path
        }
    )


async def delete_file(
    file_path: str,
    sftp: paramiko.SFTPClient,
):
    sftp.remove(file_path)
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {file_path} успешно удален",
            "file_path": file_path
        }
    )


async def get_file(file_path: str, sftp: paramiko.SFTPClient):
    with sftp.open(file_path, "rb") as remote_file:
        audio_bytes = remote_file.read()
        contents = base64.b64encode(audio_bytes).decode()
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Файл {file_path} получен успешно",
            "file_bytes": contents
        }
    )


async def files_list(sftp: paramiko.SFTPClient):
    return Response(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Список всех файлов",
            "files": sftp.listdir()
        }
    )
