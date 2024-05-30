import aiohttp


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
