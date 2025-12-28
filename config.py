import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# OpenAI API Configuration (load from environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Google Gemini API Configuration (load from environment)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Processing settings
BATCH_SIZE = 50
RATE_LIMIT_DELAY = 1
