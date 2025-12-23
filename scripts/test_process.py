import pandas as pd
import json
import time
from openai import OpenAI
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, RATE_LIMIT_DELAY

client = OpenAI(api_key=OPENAI_API_KEY)

print("Script started!")
print("Loading data...")

df = pd.read_csv('data/raw_articles.csv')
print(f"Loaded {len(df)} articles")

df = df.drop_duplicates(subset=['url'])
print(f"After removing duplicates: {len(df)} articles")

print("\nReady to process. This will take 1-2 hours.")
print("Press Ctrl+C to stop anytime.\n")

# Just process first 5 as a test
for idx, row in df.head(5).iterrows():
    print(f"Processing article {idx+1}...")
    print(f"  Title: {row['title'][:80]}")

print("\nTest complete! The full script would continue for all articles.")
