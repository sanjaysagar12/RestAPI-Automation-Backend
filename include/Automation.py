import aiohttp
import json


def extract_structure(data, structure=None):
    if structure is None:
        structure = {}
    if isinstance(data, dict):
        for key, value in data.items():
            structure[key] = {}
            extract_structure(value, structure[key])
    elif isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], (dict, list)):
            structure["list"] = []
            extract_structure(data[0], structure["list"])
        else:
            structure["list"] = None
    return structure


def compare_structures(struct1, struct2):
    if type(struct1) != type(struct2):
        return False
    if isinstance(struct1, dict):
        if struct1.keys() != struct2.keys():
            return False
        for key in struct1:
            if not compare_structures(struct1[key], struct2[key]):
                return False
    elif isinstance(struct1, list):
        if len(struct1) != len(struct2):
            return False
        for item1, item2 in zip(struct1, struct2):
            if not compare_structures(item1, item2):
                return False
    return True


class AutomationTesting:
    def __init__(self) -> None:
        pass

    async def check_status_code(self, expected_code, method, url, headers, body):
        async with aiohttp.ClientSession() as request_session:
            try:
                if method.upper() == "GET":
                    async with request_session.get(
                        url,
                        headers=headers,
                        json=body,
                    ) as response:
                        actual_code = response.status
                elif method.upper() == "POST":
                    async with request_session.post(
                        url,
                        headers=headers,
                        json=body,
                    ) as response:
                        actual_code = response.status
                elif method.upper() == "PUT":
                    async with request_session.put(
                        url,
                        headers=headers,
                        json=body,
                    ) as response:
                        actual_code = response.status
                elif method.upper() == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                        actual_code = response.status
                else:
                    return {"detail": "Unsupported HTTP method"}

                if actual_code == expected_code:
                    return {
                        "passed": True,
                        "message": "Success: The response code matches the expected code.",
                        "status_code": actual_code,
                    }

                else:
                    return {
                        "passed": False,
                        "message": "Failure: The response code does not match the expected code.",
                        "status_code": actual_code,
                    }

            except Exception as e:
                return {
                    "passed": False,
                    "detail": str(e),
                }

    async def validate_response_schema(
        self, method, url, headers, body, expected_body_schema=None
    ):
        async with aiohttp.ClientSession() as request_session:
            try:
                if method.upper() == "GET":
                    async with request_session.get(
                        url, headers=headers, json=body
                    ) as response:
                        actual_code = response.status
                        actual_body = await response.json()
                elif method.upper() == "POST":
                    async with request_session.post(
                        url, headers=headers, json=body
                    ) as response:
                        actual_code = response.status
                        actual_body = await response.json()
                elif method.upper() == "PUT":
                    async with request_session.put(
                        url, headers=headers, json=body
                    ) as response:
                        actual_code = response.status
                        actual_body = await response.json()
                elif method.upper() == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                        actual_code = response.status
                        actual_body = await response.json()
                else:
                    return {
                        "detail": "Unsupported HTTP method",
                        "passed": False,
                    }

                # Example JSON data
                json_data1 = """{
                    "name": "Alice",
                    "age": 30,
                    "address": {
                        "city": "Wonderland",
                        "zip": "12345"
                    }
                }"""

                json_data2 = """{
                    "name": "Bob",
                    "age": 25,
                    "address": {
                        "city": "Builderland",
                        "zip": "67890"
                    }
                }"""

                # # Load JSON data
                # data1 = json.loads(json_data1)
                # data2 = json.loads(json_data2)

                # Extract structures
                structure1 = extract_structure(actual_body)
                structure2 = extract_structure(expected_body_schema)

                # Compare structures
                same_structure = compare_structures(structure1, structure2)
                if same_structure:
                    return {
                        "message": "Success: The response code matches the expected code and the body matches the expected schema.",
                        "status_code": actual_code,
                        "response_body": actual_body,
                    }
                return {
                    "message": "Failure: The response body does not match the expected schema.",
                    "status_code": actual_code,
                    "response_body": actual_body,
                }

            except Exception as e:
                print({"passed": False, "detail": str(e)})
                return None
