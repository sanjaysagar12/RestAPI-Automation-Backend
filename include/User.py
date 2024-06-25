import json

from .MongoDB import MongoDB

user_collection = MongoDB("admin", "users")


class User:
    def __init__(self, email) -> None:
        self.__dict__["email"] = email

        json.dumps(self.__dict__, indent=4)

    async def get(self, key=None):
        data = await user_collection.get(
            "email",
            self.__dict__["email"],
        )
        if key:
            return data[key]
        return data

    async def set(self, key, value=None):
        if value:
            await user_collection.set(
                key=key, value=value, where={"email": self.__dict__["email"]}
            )

        await user_collection.set(key)
