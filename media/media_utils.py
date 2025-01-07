from datetime import datetime
from typing import Callable
from fastapi import UploadFile, HTTPException, status
import paramiko
from media import model
from starlette.responses import JSONResponse

async def create_unique_filepath(file: UploadFile, folder: str):
    now_str = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
    file_path = f"{folder}{now_str}_{file.filename}"
    return file_path.replace(' ', '_')

async def __get_connection(config: model.SFTPConfig):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=config.host, 
        port=config.port, 
        username=config.username, 
        password=config.password
    )
    stfp_connection = ssh.open_sftp()
    return stfp_connection, ssh



async def try_connect(
    config: model.SFTPConfig,
    on_success: Callable[[paramiko.SFTPClient, paramiko.SSHClient], JSONResponse] = None,
    on_error: Callable[[Exception], None] = None,
) -> JSONResponse:
    # Они останутся None только если __get_connection закончится с ошибкой
    # Тогда код перейдёт в блок except и on_success не вызовется с None значениями sftp и ssh
    sftp: paramiko.SFTPClient | None = None
    ssh: paramiko.SSHClient = None
    try:
        sftp, ssh = await __get_connection(config=config)
        return await on_success(sftp, ssh)
    except (IOError, FileNotFoundError) as io_e:
        if on_error:
            on_error(io_e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Файл не найден"
        )
    except Exception as e:
        if on_error:
            on_error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка подключения к файловой системе"
        )
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()