import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Create the model
model = genai.GenerativeModel('gemini-2.0-flash')

# Generate content
response = model.generate_content("Create a Chrome plugin that shows latest tweets from Andrej Karpathy, Sam Altman, and Mustafa Suleyman. Show me the file structure, show me the code for each file/ Make sure there is a readme file and instructions on how to run it and make sure it works")
print(response.text)