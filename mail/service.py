from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi import status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from auth import service as auth_service
from mail.schema import EmailSchema
import os


load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")

config = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)

mailer = FastMail(config=config)

async def send_email_message(email: str, template: str):
    message = MessageSchema(
        subject="Почтовый сервис КБНЦ РАН",
        recipients=[email],
        body=template,
        subtype=MessageType.html
    )

    try:
        await mailer.send_message(message)
        return True
    except Exception as e:
        print(e)
        raise e
    
async def send_activation_code(email: str, session: AsyncSession):
    code = await auth_service.create_reset_password_code(email, session)
    user = await auth_service.get_user_by_email(email, session)
    username: str = user.name if user else "дорогой пользователь!"
    template = f"""
        <html>
            <body>
                <p>Приветствуем, <i>{username}!<i></p>
                <p>Код для подтверждения почты и активации аккаунта: <strong>{code}</strong></p>
            </body>
        </html>
    """
    if await send_email_message(email, template):
        return Response(
            content={"success": True, "message": "Код успешно отправлен на почту"}, 
            status_code=status.HTTP_200_OK
        )
    return Response(
        content={"success": False, "message": "Ошибка отправки кода активации"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

async def send_reset_password_code(email: str, session: AsyncSession):
    code = await auth_service.create_reset_password_code(email, session)
    user = await auth_service.get_user_by_email(email, session)
    username: str = user.name if user else "дорогой пользователь!"

    template = f"""
    <html>
        <body>
            <p>Приветствуем, <i>{username}!</i></p>
            <p>Код для сброса пароля: <strong>{code}</strong></p>
            <p><strong>Никому не сообщайте его!</strong></p>
        </body>
    </html>
    """
    if await send_email_message(email, template):
        return Response(
            content={"success": True, "message": "Код успешно отправлен на почту"},
            status_code=status.HTTP_200_OK
        )
    return Response(
        content={"success": False, "message": "Ошибка отправки кода сброса пароля"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )