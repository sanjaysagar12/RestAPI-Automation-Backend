import aiosmtplib

from fastapi import HTTPException
from email.message import EmailMessage
from pydantic import EmailStr


sender_email = "nsanjaysagar205@gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = sender_email
smtp_password = "wesy nfyp cuei vibf"


class EMail:
    async def send(self, recipient_email: EmailStr, subject: str, body: str):

        message = EmailMessage()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=smtp_server,
                port=smtp_port,
                start_tls=True,
                username=smtp_username,
                password=smtp_password,
            )
            return {"message": "Email sent successfully!"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
