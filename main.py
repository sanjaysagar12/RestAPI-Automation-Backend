import asyncio
import json
import sys
import os
import datetime
import aiohttp
from pydantic import EmailStr, BaseModel, ValidationError
from quart import Quart, request, jsonify, make_response
from quart_cors import cors
from typing import Optional

root_path = os.path.dirname(__file__)

# Initialize Quart
app = Quart(__name__)
app = cors(
    app,
    allow_origin="http://localhost:8000",
    allow_credentials=True,
    allow_headers=["Content-Type"],
)


# Load configuration from config.json
with open(f"{root_path}/config.json", "r") as config_file:
    config = json.load(config_file)
sys.path.insert(1, f"{root_path}/include")

from User import User  # type: ignore
from Session import Session  # type: ignore
from Authentication import Authentication  # type: ignore
from EMail import EMail  # type: ignore
from EndPoint import EndPoint  # type: ignore
from WorkFlow import WorkFlow  # type: ignore

email = EMail()
session = Session()


# Pydantic models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class FetchOneRequest(BaseModel):
    method: str
    url: str
    headers: dict
    body: dict


class VerifyRequest(BaseModel):
    email: EmailStr
    otp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WorkFlowRequest(BaseModel):
    workflow_data: list
    automation_data: dict


async def verify_session(token, client_ip, user_agent):
    if token is None:
        return await make_response(jsonify({"detail": "Token is missing"}), 400)

    return await session.verify(token, client_ip=client_ip, user_agent=user_agent)


@app.route("/register", methods=["POST"])
async def register_user():
    try:
        data = await request.get_json()
        if data is None:
            raise TypeError("Missing JSON payload")
        request_model = RegisterRequest(**data)
    except (ValidationError, TypeError) as e:
        return await make_response(jsonify({"detail": str(e)}), 400)
    auth = Authentication()
    response = await auth.register(
        request_model.email, request_model.username, request_model.password
    )
    if response["valid"]:
        otp = response["otp"]
        await email.send(
            recipient_email=request_model.email,
            subject="OTP",
            body=str(otp),
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
        return await make_response(jsonify({"detail": str(e)}), 400)
    auth = Authentication()
    result = await auth.verify(request_model.email, request_model.otp)
    if result["valid"]:
        return jsonify({"valid": True, "message": "User verified successfully."})
    return jsonify(result)


@app.route("/login", methods=["POST"])
async def login_user():
    try:
        data = await request.get_json()
        if data is None:
            raise TypeError("Missing JSON payload")
        request_model = LoginRequest(**data)
    except (ValidationError, TypeError) as e:
        return await make_response(jsonify({"detail": str(e)}), 400)
    auth = Authentication()
    result = await auth.login(request_model.email, request_model.password)
    if result["valid"]:
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
        return jsonify({"message": "Login successful", "token": token["token"]})
    return await make_response(result, 400)


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
        return jsonify(
            {
                "valid": True,
                "message": "Token is valid.",
                "session_data": result["session_data"],
                "user_data": await user.get(),
                "client_ip": client_ip,
            }
        )
    return await make_response(jsonify({"detail": result["error"]}), 400)


@app.route("/fetch-many", methods=["POST"])
async def fetch_many():
    try:
        api_calls_data = await request.get_json()
        if api_calls_data is None or not isinstance(api_calls_data, list):
            raise TypeError("Missing or invalid JSON payload")
    except TypeError as e:
        return await make_response(jsonify({"detail": "Invalid JSON payload"}), 400)

    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if token is None:
        return await make_response(jsonify({"detail": "Token is missing"}), 400)

    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if not result["valid"]:
        return jsonify(result)

    async def make_api_call(api_call_data):
        url = api_call_data["url"]
        headers = api_call_data["headers"]
        data = api_call_data["body"]
        method = api_call_data["method"].upper()

        async with aiohttp.ClientSession() as request_session:
            if method == "GET":
                async with request_session.get(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "POST":
                async with request_session.post(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "PUT":
                async with request_session.put(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "DELETE":
                async with request_session.delete(url, headers=headers) as response:
                    return await response.json()

    # Create tasks for each API call
    tasks = [make_api_call(api_call_data) for api_call_data in api_calls_data]

    # Run tasks concurrently and gather results
    responses = await asyncio.gather(*tasks)

    return jsonify(responses)


@app.route("/fetch-one", methods=["POST"])
async def fetch_one():
    try:
        api_call_data = await request.get_json()
        if api_call_data is None:
            raise TypeError("Missing JSON payload")
    except TypeError as e:
        return await make_response(jsonify({"detail": "Invalid JSON payload"}), 400)

    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if token is None:
        return await make_response(jsonify({"detail": "Token is missing"}), 400)

    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if result["valid"]:
        url = api_call_data["url"]
        headers = api_call_data["headers"]
        data = api_call_data["body"]
        method = api_call_data["method"].upper()

        async with aiohttp.ClientSession() as request_session:
            if method == "GET":
                async with request_session.get(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "POST":
                async with request_session.post(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "PUT":
                async with request_session.put(
                    url, json=data, headers=headers
                ) as response:
                    return await response.json()

            elif method == "DELETE":
                async with request_session.delete(url, headers=headers) as response:
                    return await response.json()

    return jsonify(result)


@app.route("/save-response", methods=["POST"])
async def save_response():
    token = request.headers.get("Token")
    client_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    result = await verify_session(
        token=token,
        client_ip=client_ip,
        user_agent=user_agent,
    )
    print(result)
    if result["valid"]:
        save_data = await request.get_json()
        request_data = save_data["request"]
        response_data = save_data["response"]
        email = await session.get("email")
        api_endpoint = EndPoint(email)
        await api_endpoint.set(request=request_data, response=response_data)
        return {"valid": True, "message": "data saved"}
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
        return response_list
    return result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
