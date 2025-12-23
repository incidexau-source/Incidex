"""Final cleanup of remaining unspecified incidents."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original_count = len(df)

print("="*80)
print("FINAL CLEANUP")
print("="*80)

# 1. REMOVE INTERNATIONAL/UNCLEAR INCIDENTS
international_to_remove = [
    136,  # 16-yr-old stabbed (unclear - likely international)
    137,  # Corrective rape (unclear location)
    143,  # Die Antwoord (South Africa)
    144,  # Die Antwoord (South Africa)
    157,  # Police chief Trump (USA)
    165,  # Inyoung You (USA)
    167,  # Mexican girl (USA)
    171,  # Jussie Smollett (USA)
    127,  # Churches/mosques/synagogue (international story)
    204,  # Pharmacist UK
]

# 2. REMOVE SCOTT JOHNSON DUPLICATES
scott_johnson_duplicates = [
    179,  # Australian police arrest man for 1988 murder
    187,  # Australian arrested for homophobic killing
    193,  # Man charged in 1988 alleged hate killing
    197,  # Australian Police Make Arrest in 1988 Death
]

to_remove = international_to_remove + scott_johnson_duplicates
to_remove = [i for i in to_remove if i in df.index]

print(f"\nRemoving {len(to_remove)} international/duplicate entries:")
for idx in to_remove:
    if idx in df.index:
        title = str(df.at[idx, 'title'])[:50] if pd.notna(df.at[idx, 'title']) else 'No title'
        # Replace problematic characters
        title = title.encode('ascii', 'replace').decode('ascii')
        print(f"  - [{idx}] {title}...")

df = df.drop(to_remove)

# 3. FIX AUSTRALIAN INCIDENTS WITH COORDINATES
australian_fixes = {
    33: (-33.8131, 151.2981),   # Scott Johnson cliff (North Head, Manly)
    35: (-33.8131, 151.2981),   # Scott Johnson inquest (North Head, Manly)
    54: (-33.8688, 151.2093),   # Train threat (Sydney assumed)
    109: (-33.8688, 151.2093),  # Neo-Nazis elderly care (Sydney area)
    150: (-33.8688, 151.2093),  # Australian gay man beaten (Sydney)
    161: (-37.814, 144.963),    # Victoria homophobic past (Melbourne)
    173: (-37.814, 144.963),    # Moana Hope (Melbourne - AFL)
    175: (-33.8131, 151.2981),  # Scott Johnson $2M reward (North Head, Manly)
    176: (-33.8688, 151.2093),  # Raelene Castle death threat (Sydney)
    190: (-33.8131, 151.2981),  # Scott Johnson cliff (North Head, Manly)
    201: (-34.9281, 138.5999),  # Gay panic murder appeal (Adelaide)
}

print(f"\nFixing {len(australian_fixes)} Australian locations:")
fixed_count = 0
for idx, (lat, lon) in australian_fixes.items():
    if idx in df.index:
        title = str(df.at[idx, 'title'])[:50] if pd.notna(df.at[idx, 'title']) else 'No title'
        title = title.encode('ascii', 'replace').decode('ascii')
        df.at[idx, 'latitude'] = lat
        df.at[idx, 'longitude'] = lon
        fixed_count += 1
        print(f"  [FIXED] [{idx}] {title}...")

# Save
df.to_csv('data/incidents_in_progress.csv', index=False)

# Check remaining without coordinates
remaining_missing = df[df['latitude'].isna() | df['longitude'].isna()]

print("\n" + "="*80)
print(f"REMAINING WITHOUT COORDINATES: {len(remaining_missing)}")
print("="*80)
if len(remaining_missing) > 0:
    for idx, row in remaining_missing.iterrows():
        title = str(row['title'])[:55] if pd.notna(row['title']) else 'No title'
        location = str(row['location'])[:25] if pd.notna(row['location']) else 'No location'
        title = title.encode('ascii', 'replace').decode('ascii')
        location = location.encode('ascii', 'replace').decode('ascii')
        print(f"[{idx}] {location} | {title}")
else:
    print("All incidents now have coordinates!")

print("\n" + "="*80)
print("FINAL SUMMARY:")
print("="*80)
print(f"Original count: {original_count}")
print(f"Removed international/duplicates: {len(to_remove)}")
print(f"Fixed Australian locations: {fixed_count}")
print(f"Final count: {len(df)}")
print(f"With coordinates: {len(df) - len(remaining_missing)}")
print(f"Still missing coordinates: {len(remaining_missing)}")
print(f"Saved to: data/incidents_in_progress.csv")
