import datetime

from random import randint
from MongoDB import MongoDB
from pydantic import EmailStr
from passlib.context import CryptContext

staging_collection = MongoDB("admin", "staging")
authentication_collection = MongoDB("admin", "authentication")
users_collection = MongoDB("admin", "users")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authentication:
    def __init__(self) -> None:
        pass

    async def login(self, email: EmailStr, password: str):
        auth_data = await authentication_collection.get("email", email)
        if auth_data and pwd_context.verify(password, auth_data["password"]):
            return {"valid": True, "message": "login success"}
        return {"valid": False, "error": "invalid email or password"}

    async def register(self, email: EmailStr, username: str, password: str):
        data = await authentication_collection.is_exist(
            key="email",
            value=email,
        )
        if data:
            return {
                "valid": False,
                "error": "email already exist",
            }
        data = await authentication_collection.is_exist(
            key="username",
            value=username,
        )
        if data:
            return {
                "valid": False,
                "error": "username already exist",
            }

        hashed_password = pwd_context.hash(password)
        staging_data = await staging_collection.get("email", email)
        # Set the current date and time
        created_on = datetime.datetime.now()
        otp = randint(1000, 9999)
        # Calculate the expiry date (10 days from now)
        expire_on = created_on + datetime.timedelta(minutes=3)
        if staging_data:
            await staging_collection.set(
                key="otp",
                value=otp,
                where={"email": email},
            )
            await staging_collection.set(
                key="username",
                value=username,
                where={"email": email},
            )
            await staging_collection.set(
                key="created_on",
                value=created_on,
                where={"email": email},
            )
            await staging_collection.set(
                key="expire_on",
                value=expire_on,
                where={"email": email},
            )
            return {
                "valid": True,
                "otp": otp,
            }

        await staging_collection.set(
            {
                "email": email,
                "username": username,
                "password": hashed_password,
                "otp": otp,
                "type": "registration",
                "created_on": created_on,
                "expire_on": expire_on,
            }
        )
        return {
            "valid": True,
            "otp": otp,
        }

    async def verify(self, email: EmailStr, user_otp: int):
        staging_data = await staging_collection.get("email", email)
        otp = staging_data["otp"]
        now = datetime.datetime.now()

        # Check if the current date and time is after the expiry date
        if now > (staging_data["expire_on"]):
            return {"valid": False, "error": "otp expired"}

        if user_otp == otp:
            del staging_data["otp"]
            del staging_data["type"]
            del staging_data["created_on"]
            del staging_data["expire_on"]
            await authentication_collection.set(staging_data)
            del staging_data["password"]
            await users_collection.set(staging_data)
            await staging_collection.delete(key="email", value=email)
            return {"valid": True, "message": "User verified successfully."}
        return {"valid": False, "error": "Wrong OTP. Please try again."}
