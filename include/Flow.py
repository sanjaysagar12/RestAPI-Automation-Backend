import json

global_variable = {}
flow = {
    "request": {
        "method": "POST",
        "url": "http://localhost:8000/login",
        "variables": {
            "email": "pvtnsanjaysagar",
            "password": "12345",
        },
        "body": {
            "test1": {
                "test2": ["2", "<<email>>"],
            },
            "password": "<<password>>",
        },
        "headers": {},
    },
    "testcase": "2",
    "true": {
        "request": {
            "variables": {
                "email": "pvtnsanjaysagar",
                "password": "12345",
            },
            "method": "get",
            "url": "http://localhost:8000/profile",
        },
        "testcase": "2",
        "true": {},
        "false": {
            "true": {
                "request": {
                    "variables": {
                        "email": "pvtnsanjaysagar",
                        "password": "12345",
                    },
                    "method": "get",
                    "url": "http://localhost:8000/dashboard",
                },
                "testcase": "2",
                "true": {},
                "false": {},
            },
        },
    },
    "false": {
        "request": {
            "variables": {
                "email": "pvtnsanjaysagar",
                "password": "12345",
            },
            "method": "get",
            "url": "http://localhost:8000/register",
        },
        "testcase": "1",
        "true": {
            "request": {
                "variables": {
                    "email": "pvtnsanjaysagar",
                    "password": "12345",
                },
                "method": "get",
                "url": "http://localhost:8000/dashboard",
            },
            "testcase": "2",
            "true": {},
            "false": {},
        },
        "false": {},
    },
}


import requests


def execute_flow(flow):
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
        request_data = json.loads(request_data)
        # Extract the request data
        method = request_data["method"]
        url = request_data["url"]

    except KeyError as e:
        return

    # Send the request
    response = requests.request(method, url)
    print(response)
    # Check the testcase and decide which path to follow
    if flow["testcase"] == "1":
        next_flow = flow.get("true", {})
    else:
        next_flow = flow.get("false", {})

    # Recursively execute the next part of the flow
    execute_flow(next_flow)


# # Example usage:
# flow = {
#     # Your flow structure here
# }

execute_flow(flow)
