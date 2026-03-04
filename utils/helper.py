import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
 
from core.config import settings
 
conf = ConnectionConfig(
    MAIL_USERNAME = settings.EMAIL_ADDRESS,
    MAIL_PASSWORD = settings.EMAIL_PASSWORD,
    MAIL_FROM = settings.EMAIL_ADDRESS,
    MAIL_PORT = settings.SMTP_PORT,
    MAIL_SERVER = settings.SMTP_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
 
async def send_task_completion_email(email_to: str, task_name: str):
    html = f"""
    <p>Hello,</p>
    <p>The task <strong>{task_name}</strong> has been marked as <strong>Completed</strong>.</p>
    <p>Check your dashboard for details.</p>
    """
 
    message = MessageSchema(
        subject="Task Completed Notification",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
 
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_invite_email(email_to: str, token: str):
    html = f"""
    <p>Hello,</p>
    <p>You have been invited to join a team.</p>
    <p>Click the link below to accept the invitation:</p>
    <p>{token}</p>
    <br>
    <a href="http://localhost:8000/api/team/accept-invite/{token}">Accept Invitation</a>
    """
    message = MessageSchema(
        subject="Team Invitation",
        recipients=[email_to],
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)