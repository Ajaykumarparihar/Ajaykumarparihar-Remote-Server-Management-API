import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from . import models, schemas
from .config import settings
from typing import Optional

async def send_command_execution_email(
    user: models.User,
    server: models.RemoteServer,
    command: str,
    output: str,
    error: Optional[str],
    exit_status: int
) -> None:
    """Send an email notification about command execution."""
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_FROM
    message["To"] = user.email
    message["Subject"] = f"Command Execution Report - {server.hostname}"

    # Create email body
    body = f"""
    Command Execution Report
    
    Server: {server.hostname} ({server.ip_address})
    Command: {command}
    
    Output:
    {output}
    
    Error (if any):
    {error if error else 'None'}
    
    Exit Status: {exit_status}
    """

    message.attach(MIMEText(body, "plain"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )
    except Exception as e:
        # Log the error but don't raise it to prevent disrupting the main flow
        print(f"Failed to send email: {str(e)}") 