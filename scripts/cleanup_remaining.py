"""Clean up remaining incidents without coordinates."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original_count = len(df)

# Get incidents without coordinates
missing = df[df['latitude'].isna() | df['longitude'].isna()]
print(f"Incidents without coordinates: {len(missing)}")

# More comprehensive international keywords
international_patterns = [
    'georgia', 'bulgaria', 'cardiff', 'manchester', 'kenya', 'irish', 
    'vermont', 'brooklyn', 'new york', 'drag race uk', 'bute park',
    'karatina', 'morristown', 'rash gay bar', 'uk star', 'united kingdom'
]

# Australian locations that can be fixed
australian_fixes = {}

to_remove = []

for idx, row in missing.iterrows():
    location = str(row['location']).lower() if pd.notna(row['location']) else ''
    title = str(row['title']).lower() if pd.notna(row['title']) else ''
    combined = location + ' ' + title
    
    # Check location field
    loc_clean = str(row['location'])[:50] if pd.notna(row['location']) else 'No location'
    title_clean = str(row['title'])[:60] if pd.notna(row['title']) else 'No title'
    
    # Identify Australian vs International
    if 'adelaide' in combined:
        australian_fixes[idx] = (-34.9281, 138.5999)  # Adelaide
    elif 'queensland' in combined or 'brisbane' in combined:
        australian_fixes[idx] = (-27.4698, 153.0251)  # Brisbane
    elif 'melbourne' in combined:
        australian_fixes[idx] = (-37.814, 144.963)  # Melbourne
    elif 'sydney' in combined or 'grindr meetup in sydney' in location:
        australian_fixes[idx] = (-33.8688, 151.2093)  # Sydney
    elif 'cliff in australia' in location or 'bottom of a cliff' in location:
        australian_fixes[idx] = (-33.8131, 151.2981)  # North Head, Manly (Scott Johnson)
    elif 'roxy' in combined and 'sydney' in combined:
        australian_fixes[idx] = (-33.8688, 151.2093)  # Sydney
    elif any(pattern in combined for pattern in international_patterns):
        to_remove.append(idx)
    elif 'australia' in combined and 'australian' in title:
        australian_fixes[idx] = (-33.8688, 151.2093)  # Default Sydney
    else:
        # Check URL for hints
        url = str(row.get('url', '')).lower()
        if any(x in url for x in ['starobserver', 'abc.net.au', 'sbs.com.au', 'news.com.au', 'smh.com.au', 'theage.com.au']):
            australian_fixes[idx] = (-33.8688, 151.2093)  # Australian source, default Sydney
        else:
            to_remove.append(idx)  # Likely international or irrelevant

print(f"\nTo remove (international/irrelevant): {len(to_remove)}")
print(f"To fix (Australian): {len(australian_fixes)}")

# Remove international
print("\nRemoving:")
for idx in to_remove:
    loc = str(df.at[idx, 'location'])[:30].encode('ascii', 'replace').decode('ascii')
    title = str(df.at[idx, 'title'])[:40].encode('ascii', 'replace').decode('ascii')
    print(f"  [{idx}] {loc} | {title}...")

df = df.drop(to_remove)

# Fix Australian
print("\nFixing Australian locations:")
for idx, coords in australian_fixes.items():
    if idx in df.index:
        df.at[idx, 'latitude'] = coords[0]
        df.at[idx, 'longitude'] = coords[1]
        title = str(df.at[idx, 'title'])[:50].encode('ascii', 'replace').decode('ascii')
        print(f"  [FIXED] [{idx}] {title}... -> {coords}")

# Save
df.to_csv('data/incidents_in_progress.csv', index=False)

# Final stats
remaining = df[df['latitude'].isna() | df['longitude'].isna()]

print(f"\n{'='*60}")
print("FINAL SUMMARY")
print(f"{'='*60}")
print(f"Original: {original_count}")
print(f"Removed: {len(to_remove)}")
print(f"Fixed: {len(australian_fixes)}")
print(f"Final count: {len(df)}")
print(f"With coordinates: {len(df) - len(remaining)}")
print(f"Still missing: {len(remaining)}")

if len(remaining) > 0:
    print(f"\nStill missing coordinates:")
    for idx, row in remaining.iterrows():
        loc = str(row['location'])[:30].encode('ascii', 'replace').decode('ascii')
        title = str(row['title'])[:40].encode('ascii', 'replace').decode('ascii')
        print(f"  [{idx}] {loc} | {title}...")







