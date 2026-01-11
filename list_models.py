
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=key)

try:
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print(f"Error: {e}")
