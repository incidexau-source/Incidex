import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Try reading manually as in the main script
    try:
        with open(".env", "r", encoding="utf-8-sig") as f:
            for line in f:
                if "GOOGLE_API_KEY=" in line:
                    api_key = line.split("GOOGLE_API_KEY=", 1)[1].strip()
                    break
    except Exception as e:
        print(f"Error reading .env: {e}")

if not api_key:
    print("No API key found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    with open("models.txt", "w") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(m.name + "\n")
    print("Models written to models.txt")
except Exception as e:
    print(f"Error listing models: {e}")
