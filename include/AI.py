import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the generative AI with your API key
genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])

# Create a model instance
model = genai.GenerativeModel('gemini-pro')

user_input=input(">>")

# Generate content
response = model.generate_content(user_input)

# Print the response
print(response.text)