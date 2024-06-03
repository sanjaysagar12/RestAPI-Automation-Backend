import json
import asyncio
import aiofiles
import motor.motor_asyncio
from pymongo import ASCENDING
import time


async def load_config():
    async with aiofiles.open("config.json", "r") as config_file:
        config_data = await config_file.read()
        return json.loads(config_data)


async def ensure_indexes():
    # Load configuration from config.json asynchronously
    config = await load_config()

    # Extract database connection details
    db_config = config["database"]
    db_hostname = db_config["db_hostname"]
    db_port = db_config["db_port"]
    db_username = db_config["db_username"]
    db_password = db_config["db_password"]
    db_name = db_config["db_name"]

    # Connecting to the database
    client = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb://{db_username}:{db_password}@{db_hostname}:{db_port}/"
    )

    database = client[db_name]

    staging_collection = database.get_collection("staging")
    authentication_collection = database.get_collection("authentication")
    auth_token_collection = database.get_collection("auth_token")
    users_collection = database.get_collection("users")
    api_keys_collection = database.get_collection("api_keys")
    api_end_point_collection = database.get_collection("api_end_point")
    workspace_collection = database.get_collection("workspace")
    # Ensure unique indexes
    await staging_collection.create_index([("username", ASCENDING)], unique=True)
    await staging_collection.create_index([("email", ASCENDING)], unique=True)

    await authentication_collection.create_index([("username", ASCENDING)], unique=True)
    await authentication_collection.create_index([("email", ASCENDING)], unique=True)

    await auth_token_collection.create_index([("token", ASCENDING)], unique=True)

    await users_collection.create_index([("username", ASCENDING)], unique=True)
    await users_collection.create_index([("email", ASCENDING)], unique=True)

    await api_keys_collection.create_index([("api_key", ASCENDING)], unique=True)
    await api_keys_collection.create_index([("email", ASCENDING)], unique=True)


async def main():
    start_time = time.time()  # Record the start time
    print("Setting up Database")
    await ensure_indexes()
    end_time = time.time()  # Record the end time
    runtime = end_time - start_time  # Calculate the runtime
    print(f"Runtime: {runtime:.2f} seconds")


# Run the main function to ensure indexes and calculate runtime
asyncio.run(main())
