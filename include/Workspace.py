import json
import os
import motor.motor_asyncio
from bson.objectid import ObjectId


class WorkspaceManager:
    def __init__(self, config_path):
        # Load configuration from config.json
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        db_config = config["database"]
        db_hostname = db_config["db_hostname"]
        db_port = db_config["db_port"]
        db_username = db_config["db_username"]
        db_password = db_config["db_password"]
        db_name = db_config["db_name"]

        # Connecting to the database
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb://{db_username}:{db_password}@{db_hostname}:{db_port}/"
        )
        self.db = self.client["admin"]
        self.workspaces_collection = self.db["workspaces"]

    async def create_workspace(self, owner_email, workspace_name):
        workspace = {
            "owner": owner_email,
            "name": workspace_name,
            "collaborators": [],
            "global_variables": [],
            "folders": {},
        }
        result = await self.workspaces_collection.insert_one(workspace)
        return result.inserted_id

    async def add_collaborator(self, workspace_id, collaborator_email):
        result = await self.workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$addToSet": {"collaborators": collaborator_email}},
        )
        return result.modified_count

    async def create_folder(self, workspace_id, folder_name):
        result = await self.workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$set": {f"folders.{folder_name}": {"variables": [], "folder_data": []}}},
        )
        return result.modified_count

    async def add_global_variable(self, workspace_id, variable):
        result = await self.workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$addToSet": {"global_variables": variable}},
        )
        return result.modified_count

    async def add_folder_variable(self, workspace_id, folder_name, variable):
        result = await self.workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$addToSet": {f"folders.{folder_name}.variables": variable}},
        )
        return result.modified_count

    async def add_folder_data(self, workspace_id, folder_name, folder_data):
        result = await self.workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$push": {f"folders.{folder_name}.folder_data": folder_data}},
        )
        return result.modified_count

    async def add_local_variable(
        self, workspace_id, folder_name, request_id, local_variable
    ):
        result = await self.workspaces_collection.update_one(
            {
                "_id": ObjectId(workspace_id),
                f"folders.{folder_name}.folder_data._id": request_id,
            },
            {
                "$set": {
                    f"folders.{folder_name}.folder_data.$.local_variables.{list(local_variable.keys())[0]}": list(
                        local_variable.values()
                    )[
                        0
                    ]
                }
            },
        )
        return result.modified_count


# Usage examples
import asyncio


async def main():
    root_path = os.path.dirname(__file__)
    config_path = f"{root_path}/../config.json"
    manager = WorkspaceManager(config_path)

    # Create a new workspace
    workspace_id = await manager.create_workspace("admin@example.com", "My Workspace")
    print(f"New workspace created with ID: {workspace_id}")

    # Add a collaborator to the workspace
    modified_count = await manager.add_collaborator(
        workspace_id, "collaborator@example.com"
    )
    print(f"Collaborator added: {modified_count} document(s) modified")

    # Create a new folder in the workspace
    modified_count = await manager.create_folder(workspace_id, "new_folder")
    print(f"New folder created: {modified_count} document(s) modified")

    # Add a global variable to the workspace
    modified_count = await manager.add_global_variable(workspace_id, {"var1": 100})
    print(f"Global variable added: {modified_count} document(s) modified")

    # Add a variable to a specific folder
    modified_count = await manager.add_folder_variable(
        workspace_id, "new_folder", {"var2": 200}
    )
    print(f"Folder variable added: {modified_count} document(s) modified")

    # Add data to a specific folder
    folder_data = {
        "_id": "unique_id_123",
        "request": {
            "method": "post",
            "url": "http://example.com",
            "header": "Content-Type: application/json",
            "body": '{"key": "value"}',
        },
        "response": {
            "token": "example_token",
            "valid": True,
        },
        "local_variables": {},
    }
    modified_count = await manager.add_folder_data(
        workspace_id, "new_folder", folder_data
    )
    print(f"Folder data added: {modified_count} document(s) modified")

    # Add a new local variable to the specific request within the folder
    local_variable = {"local_var3": "value3"}
    modified_count = await manager.add_local_variable(
        workspace_id, "new_folder", "unique_id_123", local_variable
    )
    print(f"Local variable added: {modified_count} document(s) modified")


# Run the main function
asyncio.run(main())
