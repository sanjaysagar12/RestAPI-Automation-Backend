import asyncio
import json
import aiohttp
from Automation import AutomationTesting

# Global variable to store shared data
global_variable = {}

# Define the flow of API calls and tests
flow = {
    "tag": "login",
    "request": {
        "method": "POST",
        "url": "http://localhost:8000/login",
        "variables": {
            "email": "pvtnsanjaysagar@gmail.com",
            "password": "12345",
        },
        "body": {
            "email": "<<email>>",
            "password": "<<password>>",
        },
        "headers": {},
    },
    "testcase": [
        {
            "case": "check_status_200",
            "data": None,
        },
        {
            "case": "set_global_variable",
            "data": {"var": 1},
        },
        {
            "case": "set_global_variable_from_response",
            "data": {
                "key": "token",
                "value": "response['token']",
            },
        },
    ],
    "true": {
        "tag": "profile",
        "request": {
            "variables": {},
            "method": "POST",
            "url": "http://localhost:8000/profile",
            "headers": {"Token": "<<token>>"},
        },
        "testcase": [
            {
                "case": "check_status_200",
                "data": None,
            },
        ],
        "true": {},
        "false": {
            "tag": "dashboard",
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
                    "case": "check_status_200",
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
        "tag": "register",
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
            "tag": "dashboard2",
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

flow_response = list()


# Function to execute the flow of API calls and tests
async def execute_flow(flow):

    if not flow:
        print("End of flow.")
        return

    try:
        # Prepare the request data
        local_variables = flow["request"]["variables"]
        request_data = json.dumps(flow["request"])

        # Replace placeholders with actual values
        for variable, value in local_variables.items():
            request_data = request_data.replace(f"<<{variable}>>", value)

        for variable, value in global_variable.items():
            request_data = request_data.replace(f"<<{str(variable)}>>", str(value))

        request_data = json.loads(request_data)
        method = request_data["method"]
        url = request_data["url"]
        headers = request_data.get("headers", {})

        body = request_data.get("body", {})
        try:
            # Send the request and get the response
            async with aiohttp.ClientSession() as session:
                response = await send_request(session, method, url, headers, body)
                response_data = await response.json()
        except aiohttp.client_exceptions.ContentTypeError as e:
            response_data = await response.text()
        # Run test cases
        test_cases = flow["testcase"]

        automation_testing = AutomationTesting(response)
        test_result = await automation_testing.run(test_cases)
        if test_result["global_variables"] != {}:
            global_variable.update(test_result["global_variables"])
        is_passed = test_result["passed_all"]

        # Log the results
        tag = flow["tag"]
        log_flow_response(tag, response_data, test_result)

        # Determine the next flow based on the test result
        next_flow = flow["true"] if is_passed else flow.get("false", {})
        await execute_flow(next_flow)

    except aiohttp.client_exceptions.ClientConnectorError as e:
        print(f"Connection error: {e}")
        log_flow_response(flow["tag"], f"Cannot connect to host at {url}", None)


# Helper function to send HTTP requests
async def send_request(session, method, url, headers, body):
    method = method.upper()
    if method == "GET":
        return await session.get(url, headers=headers, json=body)
    elif method == "POST":
        return await session.post(url, headers=headers, json=body)
    elif method == "PUT":
        return await session.put(url, headers=headers, json=body)
    elif method == "DELETE":
        return await session.delete(url, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method")


# Helper function to log the flow response
def log_flow_response(tag, response_data, test_result):
    flow_response.append(
        {"tag": tag, "response": response_data, "test_result": test_result}
    )


# Main function to start the flow execution
async def main():
    await execute_flow(flow)
    print(json.dumps({"flow_response": flow_response}, indent=4))


# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())
