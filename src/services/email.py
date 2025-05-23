from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_reset_password_email(email: EmailStr, password: str) -> None:
    """
    Send password reset email to the specified email address with temporary password.

    Args:
        email (EmailStr): Email address to verify.
        password (str): Temporary password.
    """
    try:
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            template_body={"password": password},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="forgot_password_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    Send verification email to the specified email address to confirm its ownership by `username`.

    Args:
        email (EmailStr): Email address to verify.
        username (str): Username that claims ownership of the email address.
        host (str): Application base URL.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Verify Email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
