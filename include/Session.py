import secrets
import datetime

from .MongoDB import MongoDB

session_collection = MongoDB("admin", "session")


class Session:
    def __init__(self) -> None:
        pass

    async def start(self):
        token = secrets.token_hex(16)
        print(token)
        await session_collection.set({"token": token})
        self.__dict__["token"] = token
        return {"token": token}

    async def destroy(self):
        await session_collection.delete(key="token", value=self.__dict__["token"])

    async def get(self, key=None):

        data = await session_collection.get(key="token", value=self.__dict__["token"])

        if data:
            if key:
                return data[key]
            return data
        return None

    async def set(self, key, value=True):
        await session_collection.set(
            key=key,
            value=value,
            where={
                "token": self.__dict__["token"],
            },
        )

    async def verify(self, token, client_ip, user_agent):
        self.__dict__["token"] = token
        is_valid = await self.get()
        if is_valid:
            # Get the current date and time
            now = datetime.datetime.now()

            # Check if the current date and time is after the expiry date
            if now > datetime.datetime.fromisoformat(is_valid["expire_on"]):
                return {"valid": False, "error": "token expired"}
            # To prevent session hijacking
            if is_valid["client_ip"] != client_ip:
                return {
                    "valid": False,
                    "error": "change in IP",
                }
            if is_valid["user_agent"] != user_agent:
                return {
                    "valid": False,
                    "error": "change in user-agent",
                }
            return {
                "valid": True,
                "session_data": is_valid,
            }
        return {
            "valid": False,
            "error": "invalid token",
        }
