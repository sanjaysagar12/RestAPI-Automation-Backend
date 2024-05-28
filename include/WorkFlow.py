import aiohttp
import re


def split_data(input_string):
    """
    Splits and converts values inside parentheses.

    Args:
        input_string (str): String containing values inside parentheses to be split and converted.

    Returns:
        list: List of extracted values with their types.
    """
    # Regular expression pattern to match values inside parentheses
    pattern = r"\((.*?)\)"
    # Matching using regular expression
    matches = re.findall(pattern, input_string)
    values_with_types = []

    for match in matches:
        if ":" in match:
            value, data_type = match.split(":")
            if data_type == "int":
                value = int(value)
            elif data_type == "float":
                value = float(value)
            values_with_types.append(value)
        else:
            values_with_types.append(match)

    return values_with_types


def replace_values(workflow_data, replacement_data):
    """
    Replaces placeholders in the workflow data with actual values.

    Args:
        workflow_data (list): List of workflow steps.
        replacement_data (dict): Dictionary with replacement values.

    Returns:
        list: Updated workflow data with placeholders replaced.
    """
    for entry in workflow_data:
        tag = entry["tag"]
        if tag in replacement_data:
            replacements = replacement_data[tag]
            # Replace placeholders in headers, body, and cookies
            entry["headers"] = {
                k: replacements.get(v, v) for k, v in entry["headers"].items()
            }
            entry["body"] = {
                k: replacements.get(v, v) for k, v in entry["body"].items()
            }
            entry["cookies"] = {
                k: replacements.get(v, v) for k, v in entry["cookies"].items()
            }
    return workflow_data


def update_replacements(tag, response, automation_data, replacement_data):
    """
    Updates the replacement data based on the automation rules and API response.

    Args:
        tag (str): Tag of the current API call.
        response (dict): Response from the API call.
        automation_data (dict): Automation data containing replacement rules.
        replacement_data (dict): Dictionary to store replacement values.
    """
    if tag in automation_data:
        for hash_key in automation_data[tag]:
            keys_to_replace = automation_data[tag][hash_key][0]
            next_tag = automation_data[tag][hash_key][1]
            # Extract the necessary data from the response
            for key in keys_to_replace:
                data = response[key]
                # Update the replacement data dictionary
                if next_tag in replacement_data:
                    replacement_data[next_tag][hash_key] = data
                else:
                    replacement_data[next_tag] = {hash_key: data}


def generate_replacement_data(automation_data):
    """
    Generates initial replacement data from automation rules.

    Args:
        automation_data (dict): Automation data containing replacement rules.

    Returns:
        dict: Initial replacement data.
    """
    replacement_data = {}
    for tag in automation_data:
        for hash_key in automation_data[tag]:
            # Split and process the keys to replace
            automation_data[tag][hash_key][0] = split_data(
                automation_data[tag][hash_key][0]
            )
            if hash_key in replacement_data:
                replacement_data[hash_key].update({hash_key: "value"})
            else:
                replacement_data[hash_key] = {hash_key: "value"}
    return replacement_data


class WorkFlow:
    """
    Workflow class to handle asynchronous API calls and workflow execution.
    """

    async def api_call(self, api_call, session):
        """
        Makes an async API call and returns the response.

        Args:
            api_call (dict): Dictionary containing API call details.
            session (aiohttp.ClientSession): aiohttp session for making the request.

        Returns:
            dict: JSON response from the API call or None if the request fails.
        """
        method = api_call["method"]
        url = api_call["url"]
        headers = api_call["headers"]
        body = api_call["body"]
        cookies = api_call["cookies"]

        try:
            async with session.request(
                method, url, headers=headers, json=body, cookies=cookies
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Request failed: {e}")
            return None

    async def execute(self, workflow_data, automation_data):
        """
        Executes the workflow by making async API calls and handling automation data.

        Args:
            workflow_data (list): List of workflow steps.
            automation_data (dict): Automation data containing replacement rules.

        Returns:
            list: List of responses from the API calls.
        """
        async with aiohttp.ClientSession() as session:
            response_list = []
            replacement_data = generate_replacement_data(automation_data)

            for request_data in workflow_data:
                response = await self.api_call(request_data, session)
                if response:
                    response_list.append(response)
                    if request_data["tag"] in automation_data:
                        update_replacements(
                            request_data["tag"],
                            response,
                            automation_data,
                            replacement_data,
                        )
                        workflow_data = replace_values(workflow_data, replacement_data)

            return response_list
