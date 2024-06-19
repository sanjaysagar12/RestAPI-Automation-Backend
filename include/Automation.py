import time
import aiohttp
import json
import asyncio
import re
import xmltodict

import re


def extract_elements(input_string):
    # Use regular expression to find all elements inside square brackets
    elements = re.findall(r"\[([^\]]+)\]", input_string)
    for i in range(len(elements)):

        elements[i] = eval(elements[i])

    return elements


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
    def __init__(self, response) -> None:

        self.response = response

    async def validate_response_schema(self, expected_body_schema):
        actual_body = await self.response.json()
        # Extract structures
        structure1 = extract_structure(actual_body)
        structure2 = extract_structure(expected_body_schema)

        # Compare structures
        same_structure = compare_structures(structure1, structure2)
        if same_structure:
            return {
                "passed": True,
                "message": "Success: The response body matches the expected schema.",
                "response_body": actual_body,
            }
        return {
            "passed": False,
            "message": "Failure: The response body does not match the expected schema.",
            "response_body": actual_body,
        }

    async def validate_response_body(self, expected_body=None):
        actual_body = await self.response.json()
        if actual_body == expected_body:
            return {
                "passed": True,
                "message": "Success: The response body matches the expected body.",
                "response_body": actual_body,
            }
        return {
            "passed": False,
            "message": "Failure: The response body does not match the expected.",
            "response_body": actual_body,
        }

    async def check_valid_json(self):
        response = await self.response.text()
        try:
            # Try to parse the response as JSON
            json_response = json.dumps(response)
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

    async def check_header_element(self, expected_header_element):
        actual_headers = self.response.headers()
        if expected_header_element in actual_headers:
            return True
        return False

    async def check_html_response(self):
        response_text = await self.response.text()
        try:
            # Check if the response starts with a valid HTML tag
            html_tag_pattern = (
                r"^<\s*(!DOCTYPE\s*html|html|body|head|title|script|style)"
            )
            if re.match(html_tag_pattern, response_text, re.IGNORECASE):
                return True
            else:
                return False
        except Exception as e:
            return f"Error: {str(e)}"

    async def check_xml_response(self):
        response_text = await self.response.text()
        try:
            # Check if the response starts with an XML declaration
            xml_declaration_pattern = r'^<\?xml\s+version\s*=\s*"[^"]*"'
            if re.match(xml_declaration_pattern, response_text, re.IGNORECASE):
                return True
            else:
                return False
        except Exception as e:
            return f"Error: {str(e)}"

    async def check_json_key_value(self, key, expected_value):
        response_text = await self.response.text()
        # Check if the response is a valid JSON
        if await self.check_valid_json():
            # Parse the response as JSON
            response_json = json.loads(response_text)

            # Check if the key exists in the JSON
            if key in response_json:
                # Check if the value matches the expected value
                if response_json[key] == expected_value:
                    return {
                        "passed": True,
                        "message": "The JSON response contains the expected key-value pair.",
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"The value for the key '{key}' does not match the expected value.",
                    }
            else:
                return {
                    "passed": False,
                    "message": f"The JSON response does not contain the key '{key}'.",
                }
        else:
            return {"passed": True, "message": "The response is not in JSON format."}

    async def check_json_key(self, key="token"):
        response_text = await self.response.text()
        # Check if the response is a valid JSON
        if await self.check_valid_json():
            # Parse the response as JSON
            response_json = json.loads(response_text)

            # Check if the key exists in the JSON
            if key in response_json:
                return {
                    "passed": True,
                    "message": f"The JSON response contains the key '{key}'.",
                }
            else:
                return {
                    "passed": False,
                    "message": f"The JSON response does not contain the key '{key}'.",
                }
        else:
            return {"passed": True, "message": "The response is not in JSON format."}

    async def send_request(self, method, url, headers=None, body=None):
        async with aiohttp.ClientSession() as request_session:
            try:
                if method.upper() == "GET":
                    async with request_session.get(
                        url, headers=headers, json=body
                    ) as response:
                        status_code = response.status
                        response_body = await response.text()
                elif method.upper() == "POST":
                    async with request_session.post(
                        url, headers=headers, json=body
                    ) as response:
                        status_code = response.status
                        response_body = await response.text()
                elif method.upper() == "PUT":
                    async with request_session.put(
                        url, headers=headers, json=body
                    ) as response:
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

    async def check_status_200(self):
        if self.response.status == 200:
            return True
        return False

    async def check_status_code(self, expected_status_code=200):

        status_code = self.response.status
        if status_code == expected_status_code:
            return {
                "passed": True,
                "status_code": status_code,
            }
        else:
            return {
                "passed": False,
                "message": f"Expected status code {expected_status_code}, but got {status_code}",
                "status_code": status_code,
            }

    async def response_body_contains_string(self, expected_string=None):
        response_body = await self.response.text()
        if expected_string is not None and expected_string in response_body:
            return {
                "passed": True,
                "message": f"Response body contains the expected string: {expected_string}",
            }
        else:
            return {
                "passed": False,
                "message": f"Response body does not contain the expected string: {expected_string}",
            }

    async def response_time_less_than(self, response_time, max_time=200):
        if response_time <= max_time:
            return {
                "passed": True,
                "message": f"Success: The response time ({response_time:.2f} ms) is less than {max_time} ms.",
                "response_time": response_time,
            }
        else:
            return {
                "passed": False,
                "message": f"Failure: The response time ({response_time:.2f} ms) is not less than {max_time} ms.",
                "response_time": response_time,
            }

    async def verify_successful_post_request(self, expected_status_code=201):
        status_code = self.response.status
        if status_code == expected_status_code:
            return True
        else:
            return False

    async def convert_xml_to_json(self, response_text):
        # Check if the response is in XML format
        if (
            await self.check_xml_response(response_text)
            == "The response is in XML format."
        ):
            # Convert the XML response to a Python dictionary
            xml_dict = xmltodict.parse(response_text)

            # Convert the dictionary to a JSON string
            json_str = json.dumps(xml_dict, indent=4)

            return {
                "passed": True,
                "message": "Success: The XML response was successfully converted to a JSON object.",
                "json_object": json_str,
            }
        else:
            return {
                "passed": False,
                "message": "Failure: The response is not in XML format. Cannot convert to JSON.",
            }

    async def get_nested_element(self, keys):
        data = await self.response.json()

        try:
            for key in keys:
                data = data[key]
            return data
        except KeyError:
            return None

    async def run(self, test_case_list):
        
        previous_request = True
        case_result = {"passed_all": True, "global_variables": {}}
        for test_case in test_case_list:
            try:
                if test_case["case"] == "set_global_variable":
                    if test_case["chack_previous_case"]:
                        if previous_request:
                            case_result["global_variables"].update(test_case["data"])
                    else:
                        case_result["global_variables"].update(test_case["data"])
                    continue

                if test_case["case"] == "set_global_variable_from_response":
                    if test_case["chack_previous_case"]:
                        if previous_request:
                            key = test_case["data"]["key"]
                            extracted_elements = extract_elements(
                                test_case["data"]["value"]
                            )
                            result = await self.get_nested_element(extracted_elements)
                            case_result["global_variables"].update({key: result})
                    else:
                        key = test_case["data"]["key"]
                        extracted_elements = extract_elements(test_case["data"]["value"])
                        result = await self.get_nested_element(extracted_elements)
                        case_result["global_variables"].update({key: result})
                    continue
                # status code 200
                if test_case["case"] == "check_status_200":

                    result = await self.check_status_200()
                    case_result.update({"check_status_200": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False
                    continue

                # verify_successful_post_request
                if test_case["case"] == "verify_successful_post_request":

                    result = await self.verify_successful_post_request()
                    case_result.update({"verify_successful_post_request": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False
                    continue

                # convert_xml_to_json
                if test_case["case"] == "convert_xml_to_json":

                    result = await self.convert_xml_to_json(test_case["data"])
                    case_result.update({"convert_xml_to_json": result})

                    if not result["passed"]:
                        case_result["passed_all"] = False
                        previous_request = False

                    continue

                # response_body_contains_string
                if test_case["case"] == "response_body_contains_string":
                    data = test_case["data"]
                    result = await self.response_body_contains_string(data)
                    case_result.update({"response_body_contains_string": result})

                    if not result["passed"]:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue

                # check_status_code
                if test_case["case"] == "check_status_code":
                    data = test_case["data"]
                    result = await self.check_status_code(data)
                    case_result.update({"check_status_code": result})

                    if not result["passed"]:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue

                # check_json_key
                if test_case["case"] == "check_json_key":
                    data = test_case["data"]
                    result = await self.check_json_key(data)
                    case_result.update({"check_json_key": result})

                    if not result["passed"]:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue

                # check_json_key_value
                if test_case["case"] == "check_json_key_value":
                    data = test_case["data"]
                    result = await self.check_json_key_value(
                        key=data["key"], expected_value=data["value"]
                    )
                    case_result.update({"check_json_key_value": result})

                    if not result["passed"]:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue
                # check_xml_response
                if test_case["case"] == "check_xml_response":

                    result = await self.check_xml_response()
                    case_result.update({"check_xml_response": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue
                # check_html_response
                if test_case["case"] == "check_html_response":

                    result = await self.check_html_response()
                    case_result.update({"check_html_response": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False
                    continue

                # check_header_element
                if test_case["case"] == "check_header_element":
                    data = test_case["data"]
                    result = await self.check_header_element(data)
                    case_result.update({"check_header_element": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False

                    continue

                # check_valid_json
                if test_case["case"] == "check_valid_json":

                    result = await self.check_valid_json()
                    case_result.update({"check_valid_json": result})

                    if not result:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False
                    continue

                # validate_response_schema
                if test_case["case"] == "validate_response_schema":
                    data = test_case["data"]
                    result = await self.validate_response_schema(data)
                    case_result.update({"validate_response_schema": result})
                    print(json.dumps(result, indent=4))
                    if not result["passed"]:
                        if test_case["imp"]:
                            case_result["passed_all"] = False
                        previous_request = False
                    continue
            except Exception as e:
                case_result.update({test_case["case"]: f"Error :{e}"})
        return case_result
