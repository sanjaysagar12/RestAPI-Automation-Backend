import asyncio
import json
import os
import aiohttp
import aiosmtplib

from fastapi import HTTPException
from email.message import EmailMessage
from pydantic import EmailStr


root_path = os.path.dirname(__file__)


# Load configuration from config.json
with open(f"{root_path}/../config.json", "r") as config_file:
    config = json.load(config_file)

api_key = config["hlomail_apikey"]


class EMail:
    async def send(
        self,
        recipient_email: EmailStr,
        subject: str,
        header: str,
        body: str,
        footer: str,
    ):
        url = "https://hlomail.sanjaysagar.com/noreply-mail"
        data = {
            "api_key": api_key,
            "recipient_email": recipient_email,
            "subject": subject,
            "header": header,
            "body": body,
            "footer": footer,
            "template": "1",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                print(response.status)
                response_json = await response.json()
                print(response_json)
