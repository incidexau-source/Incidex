"""
Verify the dashboard is reading the correct data.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_FILE = DATA_DIR / "incidents_in_progress.csv"

df = pd.read_csv(CSV_FILE)
print(f"CSV file: {CSV_FILE}")
print(f"Total incidents: {len(df)}")
print(f"File exists: {CSV_FILE.exists()}")
print(f"File size: {CSV_FILE.stat().st_size / 1024:.2f} KB")
print(f"\nFirst 5 titles:")
for i, row in df.head().iterrows():
    print(f"  {i+1}. {row.get('title', '')[:60]}...")


