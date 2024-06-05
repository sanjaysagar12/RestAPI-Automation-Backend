import aiohttp
import json
import asyncio
import re


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
                    return {
                        "passed": False,
                        "detail": "Unsupported HTTP method",
                    }

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

                # Extract structures
                structure1 = extract_structure(actual_body)
                structure2 = extract_structure(expected_body_schema)

                # Compare structures
                same_structure = compare_structures(structure1, structure2)
                if same_structure:
                    return {
                        "passed": True,
                        "message": "Success: The response body matches the expected schema.",
                        "status_code": actual_code,
                        "response_body": actual_body,
                    }
                return {
                    "passed": False,
                    "message": "Failure: The response body does not match the expected schema.",
                    "status_code": actual_code,
                    "response_body": actual_body,
                }

            except Exception as e:
                print({"passed": False, "detail": str(e)})
                return None

    async def validate_response_body(
        self, method, url, headers, body, expected_body=None
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
                if actual_body == expected_body:
                    return {
                        "passed": True,
                        "message": "Success: The response body matches the expected body.",
                        "status_code": actual_code,
                        "response_body": actual_body,
                    }
                return {
                    "passed": False,
                    "message": "Failure: The response body does not match the expected.",
                    "status_code": actual_code,
                    "response_body": actual_body,
                }

            except Exception as e:
                print({"passed": False, "detail": str(e)})
                return {"passed": False}
            
    async def check_valid_json(self, response):
            try:
                # Try to parse the response as JSON
                json_response = json.loads(response)
                # If parsing succeeds, the response is in JSON format
                print("Response is in JSON format.")
                # Process the JSON response as needed
                # ...
                return True
            except json.JSONDecodeError:
                # If parsing fails, the response is not in JSON format
                print("Response is not in JSON format.")
                # Handle the non-JSON response as needed
                # ...
                return False

    async def check_header_element(self, actual_headers, expected_header_element):
            if expected_header_element in actual_headers:
                return True
            return False

    async def check_html_response(self, response_text):
        try:
            # Check if the response starts with a valid HTML tag
            html_tag_pattern = r'^<\s*(!DOCTYPE\s*html|html|body|head|title|script|style)'
            if re.match(html_tag_pattern, response_text, re.IGNORECASE):
                return "The response is in HTML format."
            else:
                return "The response is not in HTML format."
        except Exception as e:
            return f"Error: {str(e)}"
        
    async def check_xml_response(self, response_text):
        try:
            # Check if the response starts with an XML declaration
            xml_declaration_pattern = r'^<\?xml\s+version\s*=\s*"[^"]*"'
            if re.match(xml_declaration_pattern, response_text, re.IGNORECASE):
                return "The response is in XML format."
            else:
                return "The response is not in XML format."
        except Exception as e:
            return f"Error: {str(e)}"
        
    async def check_json_key_value(self, response_text, key, expected_value):
        # Check if the response is a valid JSON
        if await self.check_valid_json(response_text):
            # Parse the response as JSON
            response_json = json.loads(response_text)

            # Check if the key exists in the JSON
            if key in response_json:
                # Check if the value matches the expected value
                if response_json[key] == expected_value:
                    return "The JSON response contains the expected key-value pair."
                else:
                    return f"The value for the key '{key}' does not match the expected value."
            else:
                return f"The JSON response does not contain the key '{key}'."
        
    async def check_json_key_value(self, response_text, key="token"):
        # Check if the response is a valid JSON
        if await self.check_valid_json(response_text):
            # Parse the response as JSON
            response_json = json.loads(response_text)

            # Check if the key exists in the JSON
            if key in response_json:
                return f"The JSON response contains the key '{key}'."
            else:
                return f"The JSON response does not contain the key '{key}'."
        else:
            return "The response is not in JSON format."
        
    async def send_request(self, method, url, headers=None, body=None):
        async with aiohttp.ClientSession() as request_session:
            try:
                if method.upper() == "GET":
                    async with request_session.get(url, headers=headers, json=body) as response:
                        status_code = response.status
                        response_body = await response.text()
                elif method.upper() == "POST":
                    async with request_session.post(url, headers=headers, json=body) as response:
                        status_code = response.status
                        response_body = await response.text()
                elif method.upper() == "PUT":
                    async with request_session.put(url, headers=headers, json=body) as response:
                        status_code = response.status
                        response_body = await response.text()
                elif method.upper() == "DELETE":
                    async with request_session.delete(url, headers=headers) as response:
                        status_code = response.status
                        response_body = await response.text()
                else:
                    return {
                        "passed": False,
                        "detail": "Unsupported HTTP method",
                    }

                return {
                    "passed": True,
                    "status_code": status_code,
                    "response_body": response_body,
                }

            except Exception as e:
                return {
                    "passed": False,
                    "detail": str(e),
                }