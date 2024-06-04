import json
import os
import motor.motor_asyncio
from bson.objectid import ObjectId

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

# Connecting to the database
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb://{db_username}:{db_password}@{db_hostname}:{db_port}/"
)
db = client[db_name]
workspaces_collection = db["workspaces"]


class WorkspaceManager:

    async def create_workspace(self, owner_email, workspace_name):
        workspace = {
            "owner": owner_email,
            "name": workspace_name,
            "collaborators": [],
            "global_variables": [],
            "storage": [],
        }
        result = await workspaces_collection.insert_one(workspace)
        return str(result.inserted_id)  # Ensure the ID is returned as a string

    async def add_collaborator(self, workspace_id, collaborator_email):
        result = await workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$addToSet": {"collaborators": collaborator_email}},
        )
        return result.modified_count

    async def add_global_variable(self, workspace_id, variable):
        result = await workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$addToSet": {"global_variables": variable}},
        )
        return result.modified_count

    async def add_storage_entry(self, workspace_id, storage_entry):
        result = await workspaces_collection.update_one(
            {"_id": ObjectId(workspace_id)},
            {"$push": {"storage": storage_entry}},
        )
        return result.modified_count

    async def add_local_variable(self, workspace_id, storage_id, local_variable):
        result = await workspaces_collection.update_one(
            {
                "_id": ObjectId(workspace_id),
                "storage._id": storage_id,
            },
            {
                "$set": {
                    f"storage.$.local_variables.{list(local_variable.keys())[0]}": list(
                        local_variable.values()
                    )[0]
                }
            },
        )
        return result.modified_count

    async def change_storage_path(self, workspace_id, storage_id, new_path):
        result = await workspaces_collection.update_one(
            {
                "_id": ObjectId(workspace_id),
                "storage._id": storage_id,
            },
            {"$set": {"storage.$.path": new_path}},
        )
        return result.modified_count


# # Usage examples
# import asyncio


# async def main():
#     root_path = os.path.dirname(__file__)
#     config_path = f"{root_path}/../config.json"
#     manager = WorkspaceManager(config_path)

#     # Create a new workspace
#     workspace_id = await manager.create_workspace("admin@example.com", "My Workspace")
#     print(f"New workspace created with ID: {workspace_id}")

#     # Add a collaborator to the workspace
#     modified_count = await manager.add_collaborator(
#         workspace_id, "collaborator@example.com"
#     )
#     print(f"Collaborator added: {modified_count} document(s) modified")

#     # Add a global variable to the workspace
#     modified_count = await manager.add_global_variable(workspace_id, {"var1": 100})
#     print(f"Global variable added: {modified_count} document(s) modified")

#     # Add a storage entry to the workspace
#     storage_entry = {
#         "_id": "unique_id_123",
#         "path": "/folder1",
#         "request": {
#             "method": "post",
#             "url": "http://example.com",
#             "header": "Content-Type: application/json",
#             "body": '{"key": "value"}',
#         },
#         "response": {
#             "token": "example_token",
#             "valid": True,
#         },
#         "local_variables": {},
#     }
#     modified_count = await manager.add_storage_entry(workspace_id, storage_entry)
#     print(f"Storage entry added: {modified_count} document(s) modified")

#     # Change the path of the storage entry
#     new_path = "/new_folder"
#     modified_count = await manager.change_storage_path(
#         workspace_id, "unique_id_123", new_path
#     )
#     print(f"Storage path changed: {modified_count} document(s) modified")

#     # Add a new local variable to the specific request within the storage entry
#     local_variable = {"local_var3": "value3"}
#     modified_count = await manager.add_local_variable(
#         workspace_id, "unique_id_123", local_variable
#     )
#     print(f"Local variable added: {modified_count} document(s) modified")


# # Run the main function
# asyncio.run(main())
