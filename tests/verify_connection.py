"""
Verify Gemini Connection (Single Shot)
Runs a single article check to verify API connectivity.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts import gemini_extractor

TEST_ARTICLE = {"title": "Gay couple bashed on Oxford Street", "text": "Two men were hospitalized after a homophobic assault on Oxford Street, Sydney.", "expected": True}

def verify():
    print("Verifying Gemini Connection (Single Shot)...")
    print("-" * 50)
    
    # Wait a bit to ensure we are clear of previous rate limits
    print("Waiting 10s to clear rate limits...")
    time.sleep(10)
    
    try:
        print(f"Checking: {TEST_ARTICLE['title']}...", end=" ", flush=True)
        result = gemini_extractor.filter_article(TEST_ARTICLE['title'], TEST_ARTICLE['text'])
        
        if result == TEST_ARTICLE['expected']:
            print("PASS")
            print("  > Testing Extraction...", end=" ", flush=True)
            data = gemini_extractor.extract_incident(TEST_ARTICLE['title'], TEST_ARTICLE['text'], "http://test.com")
            if data and "incident_type" in data:
                print(f"PASS (Type: {data.get('incident_type')})")
                print("-" * 50)
                print("VERIFICATION SUCCESSFUL: API Key is valid.")
            else:
                print("FAIL (Extraction returned None)")
        else:
            print(f"FAIL (Expected {TEST_ARTICLE['expected']}, Got {result})")
            
    except Exception as e:
        print(f"ERROR: {e}")
        print("-" * 50)
        print("VERIFICATION FAILED: Exception occurred.")

if __name__ == "__main__":
    verify()
