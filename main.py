import asyncio
import json
import secrets
import sys
import os
import datetime
import aiohttp
from pydantic import EmailStr, BaseModel, ValidationError
from quart import Quart, request, jsonify, make_response
from quart_cors import cors
from typing import Any, Dict, Optional, List

root_path = os.path.dirname(__file__)

# Initialize Quart
app = Quart(__name__)
app = cors(
    app,
    allow_origin="http://localhost:5173",
    allow_credentials=True,
    allow_headers=["Content-Type", "Token"],
)



# # Load configuration from config.json
# with open(f"{root_path}/config.json", "r") as config_file:
#     config = json.load(config_file)
# sys.path.insert(1, f"{root_path}/include")

from include.Flow import FlowExecutor # type: ignore
from include.Session import Session  # type: ignore
from include.Authentication import Authentication  # type: ignore
from include.EMail import EMail  # type: ignore
from include.EndPoint import EndPoint  # type: ignore
from include.WorkFlow import WorkFlow  # type: ignore
from include.Workspace import WorkspaceManager  # type: ignore
from include.Automation import AutomationTesting  # type: ignore
from include.AI import AsyncGeminiClient # type: ignore
from include.User import User
workspacemanager = WorkspaceManager()
email = EMail()
session = Session()


# Pydantic models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class CreateWorkspaceRequest(BaseModel):
    name: str
    collaborator: Optional[List[str]] = None

class UserAiTestingRequest(BaseModel):
    user_promt: str


class SaveToWorkspaceRequest(BaseModel):
    workspace_id: str
    request: Dict
    path: str
    test_cases: Optional[List[str]] = []
    variables: Optional[Dict[str, Any]] = {}


class FetchOneRequest(BaseModel):

    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    test_cases: Optional[List] = []


class FetchManeyRequest(BaseModel):
    request_list: List
    test_cases: Optional[List] = []


class VerifyRequest(BaseModel):
    email: EmailStr
    otp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WorkFlowRequest(BaseModel):
    workflow_data: List
    automation_data: Optional[Dict[str, Any]] = None


class CheckRequestCodeRequest(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_code: int


class ValidateResponseSchemaRequest(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    expected_body_schema: Optional[Dict[str, Any]] = None


class FlowRequest(BaseModel):
    flow: Dict
    global_variable: Dict


class ValidateResponseBodyRequest(BaseModel):
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    expected_body: Optional[Dict[str, Any]] = None


class GetWorkspaceRequest(BaseModel):
    workspace_id: str


class AddCollaboratorsRequest(BaseModel):
    workspace_id: str
    collaborators: List


async def verify_session(token, client_ip, user_agent):

    return await session.verify(token, client_ip=client_ip, user_agent=user_agent)


@app.route("/register", methods=["POST"])
async def register_user():
    try:
        data = await request.get_json()
        if data is None:
            raise TypeError("Missing JSON payload")
        request_model = RegisterRequest(**data)
    except (ValidationError, TypeError) as e:
        return await make_response(jsonify({"detail": str(e)}), 401)
    auth = Authentication()
    response = await auth.register(
        request_model.email, request_model.username, request_model.password
    )
    if response["valid"]:
        otp = response["otp"]
        await email.send(
            recipient_email=[request_model.email],
            subject="OTP",
            header="Hello",
            body=f"*OTP* [>{str(otp)}<]",
            footer="thankyou",
        )
        return jsonify(
            {
                "valid": True,
                "message": "User registered successfully, please verify OTP sent to email.",
            }
        )
    return jsonify(response)


@app.route("/verify", methods=["POST"])
async def verify_user():
    try:
        data = await request.get_json()
        if data is None:
            raise TypeError("Missing JSON payload")
        request_model = VerifyRequest(**data)
    except (ValidationError, TypeError) as e:
        return await make_response(jsonify({"detail": str(e)}), 401)
    auth = Authentication()
    result = await auth.verify(request_model.email, request_model.otp)
    return jsonify(result)


@app.route("/login", methods=["POST"])
async def login_user():
    try:
        data = await request.get_json()
        if data is None:
            raise TypeError("Missing JSON payload")
        request_model = LoginRequest(**data)
    except (ValidationError, TypeError) as e:
        return await make_response(jsonify({"detail": str(e)}), 401)
    auth = Authentication()
    response = await auth.login(request_model.email, request_model.password)
    if response["valid"]:
        session = Session()
        user = User(request_model.email)
        token = await session.start()
        client_ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        created_on = datetime.datetime.now()
        expire_on = created_on + datetime.timedelta(days=10)

        # To prevent session hijacking
        await session.set("email", request_model.email)
        await session.set("client_ip", client_ip)
        await session.set("user_agent", user_agent)
        await session.set("username", await user.get("username"))

        await session.set("created_on", str(created_on))
        await session.set("expire_on", str(expire_on))
        response.update({"token": token["token"]})
        return jsonify(response)
    return await make_response(jsonify(response), 401)


@app.route("/profile", methods=["POST"])
async def profile():
    # verifying the session
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        user = User(await session.get("email"))
        return await make_response(
            jsonify(
                {
                    "valid": True,
                    "message": "Token is valid.",
                    "username": await user.get("username"),
                    "session_data": result["session_data"],
                    "user_data": await user.get(),
                    "client_ip": client_ip,
                }
            ),
            200,
        )
    return await make_response(jsonify({"detail": result["error"]}), 401)


@app.route("/fetch-many", methods=["POST"])
async def fetch_many():
    try:
        api_calls_data = await request.get_json()
        if api_calls_data is None or not isinstance(api_calls_data, list):
            raise TypeError("Missing or invalid JSON payload")
    except TypeError as e:
        return await make_response(jsonify({"detail": "Invalid JSON payload"}), 401)

    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if token is None:
        return await make_response(jsonify({"detail": "Token is missing"}), 401)

    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if not result["valid"]:
        return jsonify(result)

    async def make_api_call(api_call_data):

        url = api_call_data["url"]
        headers = api_call_data["headers"]
        data = api_call_data["body"]
        method = api_call_data["method"].upper()
        test_cases = api_call_data["test_cases"]
        tag = api_call_data["tag"]

        async with aiohttp.ClientSession() as request_session:
            try:
                if method == "GET":
                    async with request_session.get(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()

                elif method == "POST":
                    async with request_session.post(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()

                elif method == "PUT":
                    async with request_session.put(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()

                elif method == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                        response_data = await response.json()

            except aiohttp.ContentTypeError as e:
                response_data = await response.text()

            automation_testing = AutomationTesting(response)
            test_result = await automation_testing.run(test_cases)
            return {
                "tag": tag,
                "response_data": response_data,
                "test_result": test_result,
            }

    # Create tasks for each API call
    tasks = [make_api_call(api_call_data) for api_call_data in api_calls_data]

    # Run tasks concurrently and gather results
    responses = await asyncio.gather(*tasks)

    return jsonify({"valid": True, "responses": responses})


@app.route("/fetch-one", methods=["POST"])
async def fetch_one():
    try:
        api_call_data = await request.get_json()
        if api_call_data is None:
            raise TypeError("Missing JSON payload")
    except TypeError as e:
        return await make_response(jsonify({"detail": "Invalid JSON payload"}), 401)

    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if token is None:
        return await make_response(jsonify({"detail": "Token is missing"}), 401)

    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if result["valid"]:
        url = api_call_data["url"]
        headers = api_call_data["headers"]
        data = api_call_data["body"]
        method = api_call_data["method"].upper()
        api_call_data = FetchOneRequest(**api_call_data)
        async with aiohttp.ClientSession() as request_session:
            try:
                if method == "GET":
                    async with request_session.get(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()
                elif method == "POST":
                    async with request_session.post(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()
                elif method == "PUT":
                    async with request_session.put(
                        url, json=data, headers=headers
                    ) as response:
                        response_data = await response.json()
                elif method == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                        response_data = await response.json()
            except aiohttp.ContentTypeError as e:
                response_data = await response.text()

            automation_testing = AutomationTesting(response)
            test_result = await automation_testing.run(api_call_data.test_cases)

            # Integrate AI functionality
            ai_client = AsyncGeminiClient()
            ai_analysis = await ai_client.generate_content(
                response_data, api_call_data.test_cases, test_result
            )

            return {
                "valid": True,
                "response": response_data,
                "test_result": test_result,
                "ai_analysis": ai_analysis,
            }

    return jsonify(result)


@app.route("/save-to-workspace", methods=["POST"])
async def save_to_workspace():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        request_data = await request.get_json()
        save_data = SaveToWorkspaceRequest(**request_data)

        # Add a storage entry to the workspace
        storage_entry = {
            "_id": secrets.token_hex(16),
            "path": save_data.path,
            "test_cases": save_data.test_cases,
            "request": save_data.request,
            "local_variables": save_data.variables,
        }
        modified_count = await workspacemanager.add_storage_entry(
            save_data.workspace_id, storage_entry
        )
        return {"valid": True, "message": "data saved"}
    return result


@app.route("/run-flow", methods=["POST"])
async def run_flow():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        request_data = await request.get_json()
        flow_data = FlowRequest(**request_data)
        # Usage
        print("Run Flow:",flow_data.flow)
        executor = FlowExecutor()
        executor.set_global_variable(flow_data.global_variable)
        await executor.execute_flow(flow_data.flow)
        flow_result = executor.get_flow_response()

        return {"valid": True, "flow_result": flow_result}
    return result


@app.route("/history", methods=["POST"])
async def history():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        email = await session.get("email")
        api_endpoint = EndPoint(email)
        data = await api_endpoint.get()
        return {"valid": True, "data": data}
    return result


@app.route("/create-workspace", methods=["POST"])
async def create_workspace():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        response_data = await request.get_json()
        create_workflow_data = CreateWorkspaceRequest(**response_data)
        workspace_id = await workspacemanager.create_workspace(
            await session.get("email"), create_workflow_data.name
        )
        return {"valid": True, "workspace_id": workspace_id}
    return result

@app.route("/ai-testing", methods=["POST"])
async def ai_testing():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        response_data = await request.get_json()
        create_workflow_data = UserAiTestingRequest(**response_data)
        
        # Integrate AI functionality
        ai_client = AsyncGeminiClient()
        flow_data = await ai_client.generate_flow_json(create_workflow_data.user_promt)
        flow_data = flow_data.replace('```',"")
        flow_data = flow_data.replace('json',"")
        flow_data = json.loads(flow_data)
        flow_data =  flow_data['flow']
        executor = FlowExecutor()
        executor.set_global_variable({})
        await executor.execute_flow(flow_data)
        
        flow_result = executor.get_flow_response()

        return {"valid": True, "flow_result": flow_result}
    return result

@app.route("/get-workspace", methods=["POST"])
async def get_workspace():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        response_data = await request.get_json()
        workflow_data = GetWorkspaceRequest(**response_data)
        workspace_data = await workspacemanager.get_workspace(
            workflow_data.workspace_id, await session.get("email")
        )
        
        # Extracting path and _id from each item in the storage array
        extracted_data = [
            {"path": item["path"], "_id": item["_id"]}
            for item in workspace_data["storage"]
        ]
        
        return jsonify({"valid": True, "requests": extracted_data})
    
    return jsonify(result)


@app.route("/get-workspace-details/<workspace_id>/<request_id>", methods=["GET"])
async def get_workspace_details(workspace_id, request_id):
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        # Assuming workspacemanager has a method to fetch workspace details by ID
        workspace_data = await workspacemanager.get_workspace(workspace_id, await session.get("email"))

        # Find the specific request by request_id within the workspace
        request_data = None
        for item in workspace_data.get("storage", []):
            if item.get("_id") == request_id:
                request_data = item
                break
        
        if request_data:
            return jsonify({"valid": True, "request_data": request_data})
        else:
            return jsonify({"valid": False, "message": "Request not found in the workspace"})
    
    return jsonify(result)

@app.route("/get-all-workspace", methods=["GET"])
async def get_all_workspace():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        
        workspace_data = await workspacemanager.get_all_workspace(
            await session.get("email")
        )
        return {"valid": True, "workspaces": workspace_data}
    return result

@app.route("/add-collaborators", methods=["POST"])
async def add_collaborators():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        response_data = await request.get_json()
        collaborators_data = AddCollaboratorsRequest(**response_data)
        is_owner = await workspacemanager.is_owner(
            collaborators_data.workspace_id, await session.get("email")
        )
        if is_owner:
            workspace_data = await workspacemanager.add_collaborator(
                collaborators_data.workspace_id, collaborators_data.collaborators
            )
            return {"valid": True, "message": workspace_data}
        return {"valid": True, "message": "you are not the owner"}
    return result


@app.route("/workflow", methods=["POST"])
async def run_workflow():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )

    if result["valid"]:
        data = await request.get_json()
        workflow_request = WorkFlowRequest(**data)
        workflow = WorkFlow()
        response_list = await workflow.execute(
            workflow_request.workflow_data, workflow_request.automation_data
        )
        return {"valid": True, "data": response_list}
    return result


@app.route("/check-request-code", methods=["POST"])
async def check_request_code():
    # verifying the session
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        automation_testing = AutomationTesting()
        try:
            data = await request.get_json()
            if data is None:
                raise TypeError("Missing JSON payload")
            request_model = CheckRequestCodeRequest(**data)
        except (ValidationError, TypeError) as e:
            return await make_response(jsonify({"detail": str(e)}), 401)

        response = await automation_testing.check_status_code(
            expected_code=request_model.expected_code,
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            body=request_model.body,
        )
        response.update({"valid": True})
        return jsonify(response)
    return await make_response(jsonify(result), 401)


@app.route("/validate-response-schema", methods=["POST"])
async def validate_response_schema():
    # Verifying the session
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        automation_testing = AutomationTesting()
        try:
            data = await request.get_json()
            if data is None:
                raise TypeError("Missing JSON payload")
            request_model = ValidateResponseSchemaRequest(**data)
        except (ValidationError, TypeError) as e:
            return await make_response(jsonify({"detail": str(e)}), 401)

        response = await automation_testing.validate_response_schema(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            body=request_model.body,
            expected_body_schema=request_model.expected_body_schema,
        )
        response.update({"valid": True})
        return jsonify(response)
    return await make_response(jsonify(result), 401)


@app.route("/validate-response-body", methods=["POST"])
async def validate_response_body():
    # Verifying the session
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    if result["valid"]:
        automation_testing = AutomationTesting()
        try:
            data = await request.get_json()
            if data is None:
                raise TypeError("Missing JSON payload")
            request_model = ValidateResponseBodyRequest(**data)
        except (ValidationError, TypeError) as e:
            return await make_response(jsonify({"detail": str(e)}), 401)
        response = await automation_testing.validate_response_body(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            body=request_model.body,
            expected_body=request_model.expected_body,
        )

        response.update({"valid": True})
        return jsonify(response)
    return await make_response(jsonify(result), 401)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
