flow = {
    "request": {
        "method": "POST",
        "url": "http://localhost:8000/login",
        "body": {
            "email": "pvtnsanjaysagarlearn@gmail.com",
            "password": "12345",
        },
        "headers": {},
    },
    "testcase": "2",
    "true": {
        "request": {
            "method": "get",
            "url": "http://localhost:8000/profile",
        },
        "testcase": "2",
        "true": {},
        "false": {
            "true": {
                "request": {
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
            "method": "get",
            "url": "http://localhost:8000/register",
        },
        "testcase": "1",
        "true": {
            "request": {
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

    # Base case: if the flow is empty, return
    if not flow:
        return

    try:
        # Extract the request data
        method = flow["request"]["method"]
        url = flow["request"]["url"]
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
