import logging
import traceback
import json
from fastapi import Request, HTTPException
from typing import Callable
from starlette.responses import JSONResponse

default_logger_format = "%(asctime)s - %(levelname)s - %(message)s"

class KBNCLogger:
    def __init__(
        self, 
        name: str, 
        level: int = logging.DEBUG, 
        format: str = default_logger_format
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter(format)
        handler = logging.FileHandler(name)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        if not name.endswith(".log"):
            self.logger.warning(f"Log file name '{name}' does not end with '.log'.")


    async def request_log(self, request: Request, call_next):
        try:
            is_body_required = request.method not in ["GET", "DELETE"]
            body = await request.json() if is_body_required else None
            log_data = {
                "path": request.url.path,
                "method": request.method,
                "body": body
            }
            self.logger.info(log_data)
            response = await call_next(request)
            log_data["status_code"] = response.status_code
            self.logger.info(log_data)
            return response
        except HTTPException as http_exception:
            self.logger.error({
                "path": request.url.path,
                "method": request.method,
                "status_code": http_exception.status_code,
                "error": str(http_exception)
            })
        except json.decoder.JSONDecodeError as decoder_error:
            self.logger.error(
            {
                "path": request.url.path,
                "method": request.method,
                "body": "Invalid JSON",
                "detail": str(decoder_error)
            }
        )
        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")


