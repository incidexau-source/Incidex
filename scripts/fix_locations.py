"""Fix missing coordinates and remove international incidents."""
import pandas as pd

df = pd.read_csv('data/incidents_in_progress.csv')
original_count = len(df)

# 1. MANUAL FIXES FOR AUSTRALIAN LOCATIONS
manual_fixes = {
    30: (-33.874, 151.228),   # Rushcutters Bay, Sydney
    39: (-33.878, 151.219),   # Darlinghurst, Sydney (chicken shop)
    47: (-33.878, 151.219),   # Darlinghurst, Sydney (chicken shop)
    50: (-33.878, 151.212),   # Sydney gay suburbs (Surry Hills/Darlinghurst)
    84: (-37.814, 144.963),   # Melbourne
    90: (-14.466, 132.264),   # Katherine, NT (sistergirl)
    97: (-37.814, 144.963),   # Victoria (MP's daughter)
    119: (-37.375, 143.475),  # Lexton, VIC (Rainbow Serpent)
    123: (-28.814, 153.277),  # Lismore, NSW (rainbow walkway)
    132: (-33.917, 151.035),  # Bankstown, NSW
    134: (-27.469, 153.023),  # Brisbane (MCC church)
    139: (-27.535, 153.021),  # Moorooka, Brisbane
    190: (-32.529, 115.744),  # Mandurah, WA
}

fixed_count = 0
for idx, (lat, lon) in manual_fixes.items():
    if idx in df.index:
        df.at[idx, 'latitude'] = lat
        df.at[idx, 'longitude'] = lon
        fixed_count += 1
        print(f"[FIXED] Index {idx}: {df.at[idx, 'location'][:40]} -> ({lat}, {lon})")

print(f"\nFixed {fixed_count} Australian locations")

# 2. REMOVE INTERNATIONAL INCIDENTS
# Indices of international incidents to remove
international_indices = [
    65,   # synagogue (New York)
    68,   # Birmingham Gay Village (UK)
    69,   # Gay Nightclub (Colorado)
    74,   # Brianna Ghey (UK)
    80,   # Colorado LGBTQ nightclub
    96,   # Euskirchen (Germany)
    113,  # Jordan Valley (Israel)
    116,  # Dalston, London (UK)
    117,  # Chechnya (Russia)
    143,  # honeymoon flight to Egypt
    145,  # Upminster Station, London (UK)
    148,  # Peoria, Arizona (USA)
    149,  # Tel Aviv (Israel)
    153,  # Sky TV channel (UK)
    154,  # Kathy Griffin (USA)
    163,  # outside London pub (UK)
    165,  # Birmingham mosque (UK)
    181,  # St Louis county (USA)
    185,  # Melville, New York (USA)
    194,  # Croatian town
    224,  # Grande Prairie hospital (Canada)
]

# Also remove non-incidents
non_incidents = [
    141,  # Folau opinion piece
    158,  # It Chapter 2 movie scene
]

to_remove = international_indices + non_incidents
to_remove = [i for i in to_remove if i in df.index]

print(f"\nRemoving {len(to_remove)} international/non-incident entries:")
for idx in to_remove:
    if idx in df.index:
        title = str(df.at[idx, 'title'])[:50] if pd.notna(df.at[idx, 'title']) else 'No title'
        location = str(df.at[idx, 'location'])[:30] if pd.notna(df.at[idx, 'location']) else 'No location'
        print(f"  - [{idx}] {title}... ({location})")

df = df.drop(to_remove)

# 3. LIST REMAINING "NOT SPECIFIED" INCIDENTS
print("\n" + "="*80)
print("INCIDENTS WITH 'NOT SPECIFIED' OR UNKNOWN LOCATIONS:")
print("="*80)

not_specified = df[
    (df['latitude'].isna() | df['longitude'].isna()) &
    (df['location'].str.lower().str.contains('not specified|unknown|nan', na=True) |
     df['location'].isna())
]

for idx, row in not_specified.iterrows():
    title = str(row['title'])[:60]
    location = str(row['location'])[:30]
    url = str(row['url'])[:60] if pd.notna(row['url']) else 'No URL'
    print(f"\n[{idx}] {title}...")
    print(f"     Location: {location}")
    print(f"     URL: {url}...")

# Save
df.to_csv('data/incidents_in_progress.csv', index=False)

# Summary
print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
print(f"Original count: {original_count}")
print(f"Fixed Australian locations: {fixed_count}")
print(f"Removed international/non-incidents: {len(to_remove)}")
print(f"Final count: {len(df)}")
print(f"Remaining without coordinates: {df['latitude'].isna().sum()}")
print(f"Saved to: data/incidents_in_progress.csv")

