import os
import datetime
import motor.motor_asyncio, json

root_path = os.path.dirname(__file__)


# Load configuration from config.json
with open(f"{root_path}/../config.json", "r") as config_file:
    config = json.load(config_file)

db_config = config["database"]
db_hostname = db_config["db_hostname"]
db_port = db_config["db_port"]
db_username = db_config["db_username"]
db_password = db_config["db_password"]
db_name = db_config["db_name"]

# Connecting To Database
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb://{db_username}:{db_password}@{db_hostname}:{db_port}/"
)


class MongoDB(object):

    def __init__(self, database, collection: str):
        # Directly set the attributes in the instance dictionary
        self.__dict__["database"] = client[database]
        self.__dict__["collection"] = self.__dict__["database"].get_collection(
            collection
        )

    async def is_exist(self, key, value):
        data = await self.get(key=key, value=value)
        if data:
            return True
        return False

    async def delete(self, key, value):
        myquery = {key: value}

        await self.__dict__["collection"].delete_many(myquery)
        return "delated"

    async def set(self, key, value=None, where=None):
        # Update data in Database
        if value:
            myquery = where

            newvalues = {"$set": {key: value}}
            await self.__dict__["collection"].update_many(myquery, newvalues)
            return f"{key} updated to {value}"
        # Add new data in Database
        await self.__dict__["collection"].insert_one(key)
        return f"new data inserted {key}"

    async def get(self, key=None, value=None, query=None):
        if query:
            # query = {key: value}
            cursor = self.__dict__["collection"].find(query, {"_id": 0})

            results = []
            async for document in cursor:
                results.append(document)
            return results

        return await self.__dict__["collection"].find_one({key: value}, {"_id": 0})
