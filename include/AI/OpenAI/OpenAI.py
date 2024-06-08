from openai import OpenAI  #to use ai chatbot using API keys
import os   
from dotenv import load_dotenv  #to load the api key from .env




user_input= input(">>")
load_dotenv()  #unload the API keys from .env

client = OpenAI(                            #from 17 to 35 it is for to generate ai answer
    api_key=os.getenv("OPEN_API_KEY")
)

def structured_generator(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            },
        ],
        model="gpt-3.5-turbo"
    )
    return chat_completion

prompt = ( f" {user_input}")
result=structured_generator(prompt)
output=result.choices[0].message.content

print("The Output of the above Prompt is:\n",output)