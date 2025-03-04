import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from auth.router import auth_router
from mail.router import mail_router
from media.router import media_router
from words.router import dictionary_router
from suggestion.router import suggests_router
from starlette.responses import JSONResponse
from kbnc_logging.logger import KBNCLogger

kbnc_logger = KBNCLogger(name = "kbnc_logging/api_logs.log")

app = FastAPI()
app.include_router(auth_router, prefix='/auth/jwt')
app.include_router(mail_router, prefix='/mail')
app.include_router(media_router, prefix='/media')
app.include_router(dictionary_router, prefix='/dictionary')
app.include_router(suggests_router, prefix='/suggestion')

origins = ['*']
methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
headers = [
    "Content-Type",
    "Authorization",
    "Access-Control-Request-Headers",
    "Access-Control-Allow-Headers"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)


@app.head('/')
@app.get('/')
def health_check():
    return {"message": "Welcome to Bal Rus Dictionary"}

@app.middleware("http")
async def add_logger_middleware(request: Request, call_next):
    return await kbnc_logger.request_log(request, call_next) or await call_next(request)

@app.exception_handler(Exception)
async def handle_all_unhandled_exceptions(request: Request, exception: Exception):
    error_message = f"""
    Request json = {request}
    Request headers = {request.headers}
    Exception = {exception}"""
    kbnc_logger.logger.error(f"Error from handler: {error_message}")
    return JSONResponse(content={"exception": str(exception)})

if __name__ == '__main__':
    # uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True, workers=4)
    uvicorn.run('main:app', host='192.168.177.2', port=8000, reload=True, workers=4)
