import asyncio
import json
import os
import aiohttp
from google.generativeai.types import GenerateContentResponse

root_path = os.path.dirname(__file__)

def load_config(config_path='config.json'):
    with open(f"{root_path}/../config.json", "r") as config_file:
        return json.load(config_file)

config = load_config()

class AsyncGeminiClient:
    def __init__(self):
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.api_key = config['google_ai']['api_key']

    async def generate_content(self, response_data: dict, test_cases: list, test_result: dict) -> str:
        print("Gemini AI is running......")
        url = f"{self.base_url}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        prompt = f"""
        Analyze the following API response, test cases, and test results:

        API Response:
        {json.dumps(response_data, indent=2)}

        Test Cases:
        {json.dumps(test_cases, indent=2)}

        Test Results:
        {json.dumps(test_result, indent=2)}

        Please provide an analysis covering the following points:
        1. Summarize the API response structure and content.
        2. Evaluate the test results, highlighting any passed or failed tests.
        3. Identify any potential issues or anomalies in the API response.
        4. Suggest improvements or additional test cases if applicable.
        5. Provide an overall assessment of the API's performance based on these results.

        Your analysis should be concise yet comprehensive, suitable for a technical audience.
        """

        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    analysis = result['candidates'][0]['content']['parts'][0]['text']
                    print("Gemini AI Analysis:", analysis)
                    return analysis
                else:
                    error_msg = f"Error: {response.status} - {await response.text()}"
                    print(error_msg)
                    return error_msg

# async def main():
#     client = AsyncGeminiClient()
#     user_input = input(">> ")
#     response = await client.generate_content(user_input)
#     print(response)

# if __name__ == "__main__":
#     asyncio.run(main())