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

    async def generate_content(self, user_input: str) -> str:
        url = f"{self.base_url}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": user_input}]}]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return f"Error: {response.status} - {await response.text()}"

async def main():
    client = AsyncGeminiClient()
    user_input = input(">> ")
    response = await client.generate_content(user_input)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())