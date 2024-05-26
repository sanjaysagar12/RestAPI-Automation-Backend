import json
import sys
import os
import datetime
import aiohttp
from pydantic import EmailStr, BaseModel
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

root_path = os.path.dirname(__file__)

# Initialize FastAPI
app = FastAPI()

# Load configuration from config.json
with open(f"{root_path}/config.json", "r") as config_file:
    config = json.load(config_file)
sys.path.insert(1, f"{root_path}/include")

from User import User  # type: ignore
from Session import Session  # type: ignore
from Authentication import Authentication  # type: ignore
from EMail import EMail  # type: ignore

email = EMail()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class TokenRequest(BaseModel):
    token: str


@app.post("/register")
async def register_user(request: RegisterRequest):
    auth = Authentication()
    response = await auth.register(request.email, request.username, request.password)
    if response["valid"]:
        otp = response["otp"]
        await email.send(
            recipient_email=request.email,
            subject="OTP",
            body=str(otp),
        )
        return {
            "valid": True,
            "message": "User registered successfully, please verify OTP sent to email.",
        }
    return response


@app.post("/verify")
async def verify_user(request: VerifyRequest):
    auth = Authentication()
    result = await auth.verify(request.email, request.otp)
    if result["valid"]:
        return {"valid": True, "message": "User verified successfully."}
    return result


@app.post("/fetch-one")
async def fetch_one(
    request: Request,
    api_call_data: FetchOneRequest,
    token: str = Header(None),
):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    if token is None:
        raise HTTPException(status_code=400, detail="Token is missing")
    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if result["valid"]:
        url = api_call_data.url
        headers = api_call_data.headers
        data = api_call_data.body
        async with aiohttp.ClientSession() as request_session:
            if api_call_data.method == "GET":
                async with request_session.get(
                    url,
                    json=data,
                    headers=headers,
                ) as response:
                    return await response.text()

            if api_call_data.method == "POST":
                async with request_session.post(
                    url,
                    json=data,
                    headers=headers,
                ) as response:
                    return await response.text()

            if api_call_data.method == "PUT":
                async with request_session.put(
                    url,
                    json=data,
                    headers=headers,
                ) as response:
                    return await response.text()

            if api_call_data.method == "DELETE":
                async with request_session.delete(
                    url,
                    headers=headers,
                ) as response:
                    return await response.text()

    return result


@app.post("/profile")
async def profile(
    request: Request,
    token: str = Header(None),
):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    if token is None:
        raise HTTPException(status_code=400, detail="Token is missing")

    session = Session()
    result = await session.verify(token, client_ip=client_ip, user_agent=user_agent)
    if result["valid"]:
        return {
            "message": "Token is valid.",
            "userdata": result["session_data"],
            "client_ip": client_ip,
        }
    raise HTTPException(status_code=400, detail=result["error"])


@app.post("/login")
async def login_user(request: LoginRequest, fastapi_request: Request):
    auth = Authentication()
    result = await auth.login(request.email, request.password)
    print(fastapi_request)
    if result["valid"]:
        session = Session()
        token = await session.start()
        client_ip = fastapi_request.client.host
        user_agent = fastapi_request.headers.get("user-agent")
        # To Provent from Session hijacking
        await session.set("email", request.email)
        await session.set("client_ip", client_ip)
        await session.set("user_agent", user_agent)
        created_on = datetime.datetime.now()
        expire_on = created_on + datetime.timedelta(days=10)
        await session.set("created_on", str(created_on))
        await session.set("expire_on", str(expire_on))
        return {"message": "Login successful", "token": token["token"]}
    raise HTTPException(status_code=400, detail="Invalid email or password")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
