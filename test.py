import json
import sys
import os


root_path = os.path.dirname(__file__)


# Load configuration from config.json
with open(f"{root_path}/config.json", "r") as config_file:
    config = json.load(config_file)
sys.path.insert(1, config["include"])

from MongoDB import MongoDB  # type: ignore


import asyncio


async def main():

    db = MongoDB("admin", "authentication")
    data = await db.is_exist(key="email", value="sanjaysagarlearn@gmsail.com")
    print(data)


asyncio.run(main())
