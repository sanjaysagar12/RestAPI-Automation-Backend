import json

from MongoDB import MongoDB

user_collection = MongoDB("admin", "users")


class User:
    def __init__(self, username) -> None:
        self.__dict__["username"] = username

        json.dumps(self.__dict__, indent=4)

    async def get(self, key):
        data = await user_collection.get(
            "username",
            self.__dict__["username"],
        )

        return data[key]

    async def set(self, key, value=None):
        if value:
            await user_collection.set(
                key=key, value=value, where={"username": self.__dict__["username"]}
            )

        await user_collection.set(key)
