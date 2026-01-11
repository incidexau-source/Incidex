
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
# Force vertexai=False to ensure it uses the Gemini API (AI Studio)
client = genai.Client(api_key=key, vertexai=False)

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Hello'
    )
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
