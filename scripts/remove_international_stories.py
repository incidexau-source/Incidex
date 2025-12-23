"""Remove international stories that were incorrectly kept."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original = len(df)

# International story keywords in titles (not Australian incidents)
international_title_keywords = [
    'nigeria', 'iran', 'utah', 'oklahoma', 'colorado', 'k-pop', 'k - pop',
    'stoning', 'death by stoning', 'fbi arrests', 'new york', 'club q',
    'texas', 'hindu temple', 'kentucky', 'idaho', 'florida', 'tennessee',
    'mississippi', 'alabama', 'georgia shooting', 'virginia', 'ohio',
    'michigan', 'wisconsin', 'minnesota', 'indiana', 'louisiana'
]

to_remove = []

for idx, row in df.iterrows():
    title = str(row['title']).lower() if pd.notna(row['title']) else ''
    location = str(row['location']).lower() if pd.notna(row['location']) else ''
    
    # Check for international stories
    if any(kw in title for kw in international_title_keywords):
        to_remove.append(idx)
        title_display = str(row['title'])[:60].encode('ascii', 'replace').decode('ascii')
        print(f"REMOVE [{idx}]: {title_display}...")

print(f"\nTotal to remove: {len(to_remove)}")

# Remove them
df = df.drop(to_remove)
df.to_csv('data/incidents_in_progress.csv', index=False)

print(f"\nOriginal: {original}")
print(f"Removed: {len(to_remove)}")
print(f"Final: {len(df)}")







