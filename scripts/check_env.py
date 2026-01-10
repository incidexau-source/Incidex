
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
print(f"Checking .env at: {env_path}")
print(f"Exists: {env_path.exists()}")

if env_path.exists():
    with open(env_path, 'r') as f:
        lines = f.readlines()
        print(f"File has {len(lines)} lines.")
        for line in lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                print(f"Found key: {key}")

load_dotenv(dotenv_path=env_path)
print(f"GOOGLE_API_KEY in env: {'GOOGLE_API_KEY' in os.environ}")
