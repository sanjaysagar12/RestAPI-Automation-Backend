import asyncio
import json

global_variable = {}
flow = {
    "tag":"login",
    "request": {
        "method": "POST",
        "url": "http://localhost:8000/login",
        "variables": {
            "email": "pvtnsanjaysagar@gmail.com",
            "password": "12345",
        },
        "body": {
            "email":"<<email>>",
            "password": "<<password>>",
        },
        "headers": {},
    },
    "testcase": [
        {
            "case": "chack_status_200",
            "data": None,
        },
      
    ],
    "true": {
        "tag":"profile",
        "request": {
            "variables": {
                "email": "pvtnsanjaysagar",
                "password": "12345",
            },
            "method": "get",
            "url": "http://localhost:8000/profile",
        },
        "testcase": [
            {
                "case": "chack_status_200",
                "data": None,
            },
            {
                "case": "chack_status_200",
                "data": {
                    "valid": True,
                    "token": "dkqnweoidj2939023i0923u09",
                },
            },
        ],
        "true": {},
        "false": {
            
                "tag":"dashboard",
                "request": {
                    "variables": {
                        "email": "pvtnsanjaysagar",
                        "password": "12345",
                    },
                    "method": "get",
                    "url": "http://localhost:8000/dashboard",
                },
                "testcase": [
                    {
                        "case": "chack_status_200",
                        "data": None,
                    },
                    {
                        "case": "check_body_shema",
                        "data": {
                            "valid": True,
                            "token": "dkqnweoidj2939023i0923u09",
                        },
                    },
                ],
                "true": {},
                "false": {},
        },
    },
    "false": {
        "tag":"register",
        "request": {
            "variables": {
                "email": "pvtnsanjaysagar",
                "password": "12345",
            },
            "method": "get",
            "url": "http://localhost:8000/register",
        },
        "testcase": [
            {
                "case": "check_sataus_200",
                "data": None,
            },
            {
                "case": "check_body_shema",
                "data": {
                    "valid": True,
                    "token": "dkqnweoidj2939023i0923u09",
                },
            },
        ],
        "true": {
            "tag":"dashboard2",
            "request": {
                "variables": {
                    "email": "pvtnsanjaysagar",
                    "password": "12345",
                },
                "method": "get",
                "url": "http://localhost:8000/dashboard",
            },
            "testcase": [
                {
                    "case": "check_sataus_200",
                    "data": None,
                },
                {
                    "case": "check_body_shema",
                    "data": {
                        "valid": True,
                        "token": "dkqnweoidj2939023i0923u09",
                    },
                },
            ],
            "true": {},
            "false": {},
        },
        "false": {},
    },
}


import aiohttp
import requests
from Automation import AutomationTesting

flow_response = []


async def execute_flow(flow):
    test_result = []

    if flow == {}:
        print("end")
        return
    try:

        local_variables = flow["request"]["variables"]
        request_data = flow["request"]
        request_data = json.dumps(request_data)

        for variable in local_variables:
            request_data = request_data.replace(
                f"<<{variable}>>", local_variables[variable]
            )
        for variable in global_variable:
            request_data = request_data.replace(
                f"<<{variable}>>", local_variables[variable]
            )

        request_data = json.loads(request_data)
        test_cases = flow["testcase"]
        tag = flow["tag"]
        # Extract the request data
        method = request_data["method"]
        url = request_data["url"]
        headers = request_data["headers"]
        body = request_data['body']
    except KeyError as e:
        print(e)
        headers = {}
        body = {}
       

    # Send the request
    try:
        async with aiohttp.ClientSession() as request_session:
            try:
                if method.upper() == "GET":
                    async with request_session.get(url, headers=headers, json=body) as response:
                    
                        response_data = await response.json()
                elif method.upper() == "POST":
                    async with request_session.post(url, headers=headers, json=body) as response:
                      
                        response_data = await response.json()
                elif method.upper() == "PUT":
                    async with request_session.put(url, headers=headers, json=body) as response:
                       
                        response_data = await response.json()
                elif method.upper() == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                  
                        response_data = await response.json()
                else:
                    return {
                        "passed": False,
                        "detail": "Unsupported HTTP method",
                    }


            except aiohttp.ContentTypeError as e:
                response_data = await response.text()
            
        automationtesting = AutomationTesting(response)
    
        data = await automationtesting.run(test_cases)
        is_passed = data["passed_all"]
       
        test_result.append(data)
        flow_response.append({
            "tag":tag,
            "response":response_data,
            "test_result":test_result
        })
      
        # Check the testcase and decide which path to follow
        if is_passed:
            next_flow = flow.get("true", {})
        else:
            next_flow = flow.get("false", {})

        # Recursively execute the next part of the flow
        await execute_flow(next_flow)
    except aiohttp.client_exceptions.ClientConnectorError as e:
        print(e)
        flow_response.append({
            "tag":tag,
            "response":f"Cannot connect to host at {url}",
            "test_result":None
        })
        return f"Cannot connect to host at {url}"


# # Example usage:
# flow = {
#     # Your flow structure here
# }


async def main():
    await execute_flow(flow)

    print(json.dumps({"flow_response":flow_response},indent=4))
asyncio.run(main())
