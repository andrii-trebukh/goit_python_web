from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="REST API app",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three arguments:
            1) An EmailStr object containing the user's email address.
            2) A string containing the username of the user who is registering for an account.  This will be used in a template message that is sent to them via FastMail API.
            3) A string containing hostname of where this application is hosted (e.g., &quot;localhost&quot; or &quot;127.0.0.&quot;).  This will be used in a template message that is sent to them via FastMail API
    
    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the email template
    :param host: str: Pass the host url to the email template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(email: EmailStr, username: str, host: str):
    """
    The send_reset_password_email function sends an email to the user with a link to reset their password.
    
    :param email: EmailStr: Specify the email address of the user who requested a password reset
    :param username: str: Pass the username of the user to the template
    :param host: str: Pass the hostname of the website to be used in the email
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_reset = await auth_service.create_password_reset_token({"sub": email})
        message = MessageSchema(
            subject="Paasword reset request",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_reset},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password_email_template.html")
    except ConnectionErrors as err:
        print(err)
