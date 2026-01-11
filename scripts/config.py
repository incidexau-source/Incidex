
import os
from pathlib import Path
from dotenv import load_dotenv

# Define base directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
if ENV_PATH.exists():
    # Attempt to load with dotenv (standard)
    load_dotenv(dotenv_path=ENV_PATH)
    
    # Fallback if GOOGLE_API_KEY is still missing (BOM handle)
    if not os.getenv("GOOGLE_API_KEY"):
        try:
            with open(ENV_PATH, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    if "GOOGLE_API_KEY=" in line:
                        key = line.split("GOOGLE_API_KEY=", 1)[1].strip()
                        # Remove quotes if present
                        if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
                            key = key[1:-1]
                        os.environ["GOOGLE_API_KEY"] = key
                        break
        except Exception:
            pass

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# AI Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Search Configuration
START_YEAR = 2005
END_YEAR = 2025

# Processing settings
BATCH_SIZE = 50
RATE_LIMIT_DELAY = 1.0

# Folders
DATA_DIR = os.path.join(BASE_DIR, "data")

# Output Files
PHASE1_OUTPUT = os.path.join(DATA_DIR, "phase1_incidents.csv")
CLEANED_OUTPUT = os.path.join(DATA_DIR, "cleaned_incidents_in_progress.csv")
INTL_EXCLUSIONS = os.path.join(DATA_DIR, "international_incidents_removed.csv")
CLEANUP_REPORT = os.path.join(DATA_DIR, "cleanup_report.txt")
