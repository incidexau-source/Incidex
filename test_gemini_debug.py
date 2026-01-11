
import google.genai as genai
import os
print(f"GenAI File: {genai.__file__}")

from google.genai import Client
key = os.getenv("GOOGLE_API_KEY")
print(f"Key present: {bool(key)}")
try:
    client = Client(api_key=key)
    print("Client initialized")
except Exception as e:
    print(f"Client error: {e}")
