"""Final comprehensive cleanup of all remaining issues."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original_count = len(df)

print("="*80)
print("COMPREHENSIVE CLEANUP")
print("="*80)

# Get incidents without coordinates
missing = df[df['latitude'].isna() | df['longitude'].isna()]
print(f"\nIncidents without coordinates: {len(missing)}")

# Categorize by location
international_keywords = [
    'london', 'uk', 'england', 'birmingham', 'new york', 'usa', 'u.s.', 
    'united states', 'new zealand', 'canada', 'poland', 'russia', 'china',
    'israel', 'tel aviv', 'chechnya', 'egypt', 'mexico', 'croatia', 'spain',
    'finland', 'ireland', 'peoria', 'st louis', 'melville', 'northampton',
    'royal holloway', 'newquay', 'grande prairie', 'jordan valley', 'upminster'
]

unusable_keywords = [
    'not specified', 'unknown', 'nan', 'not mentioned', 'sky tv', 
    'honeymoon flight', 'churches, mosques', 'outside synagogue'
]

to_remove = []
to_fix = []
truly_unknown = []

for idx, row in missing.iterrows():
    location = str(row['location']).lower() if pd.notna(row['location']) else 'nan'
    title = str(row['title']).lower() if pd.notna(row['title']) else ''
    
    # Check if international
    is_international = any(kw in location for kw in international_keywords)
    
    # Check if unusable location
    is_unusable = any(kw in location for kw in unusable_keywords) or location == 'nan'
    
    # Check if title suggests Australian content
    is_australian_content = any(kw in title for kw in ['australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'queensland', 'victoria', 'nsw'])
    
    if is_international:
        to_remove.append(idx)
    elif is_unusable and not is_australian_content:
        to_remove.append(idx)
    elif is_unusable and is_australian_content:
        # Australian content with vague location - try to fix
        to_fix.append((idx, row))
    else:
        truly_unknown.append((idx, row))

print(f"\nInternational/unusable to remove: {len(to_remove)}")
print(f"Australian with vague location (to fix): {len(to_fix)}")
print(f"Unknown (needs review): {len(truly_unknown)}")

# Remove international/unusable
print("\n" + "-"*80)
print("REMOVING INTERNATIONAL/UNUSABLE:")
for idx in to_remove[:20]:  # Show first 20
    loc = str(df.at[idx, 'location'])[:30].encode('ascii', 'replace').decode('ascii')
    title = str(df.at[idx, 'title'])[:40].encode('ascii', 'replace').decode('ascii')
    print(f"  [{idx}] {loc} | {title}...")
if len(to_remove) > 20:
    print(f"  ... and {len(to_remove) - 20} more")

df = df.drop(to_remove)

# Fix Australian incidents with default coordinates
print("\n" + "-"*80)
print("FIXING AUSTRALIAN INCIDENTS WITH DEFAULT COORDS:")

# Default to Sydney CBD for vague Australian locations
SYDNEY_DEFAULT = (-33.8688, 151.2093)
MELBOURNE_DEFAULT = (-37.814, 144.963)

fixed_count = 0
for idx, row in to_fix:
    if idx not in df.index:
        continue
    title = str(row['title']).lower()
    
    # Try to determine location from title
    if 'melbourne' in title or 'victoria' in title:
        coords = MELBOURNE_DEFAULT
    else:
        coords = SYDNEY_DEFAULT  # Default to Sydney
    
    df.at[idx, 'latitude'] = coords[0]
    df.at[idx, 'longitude'] = coords[1]
    fixed_count += 1
    
    title_display = str(row['title'])[:50].encode('ascii', 'replace').decode('ascii')
    print(f"  [FIXED] [{idx}] {title_display}... -> {coords}")

# Show truly unknown
print("\n" + "-"*80)
print(f"REMAINING UNKNOWN ({len(truly_unknown)}):")
for idx, row in truly_unknown[:15]:
    if idx in df.index:
        loc = str(row['location'])[:25].encode('ascii', 'replace').decode('ascii')
        title = str(row['title'])[:45].encode('ascii', 'replace').decode('ascii')
        print(f"  [{idx}] {loc} | {title}...")
if len(truly_unknown) > 15:
    print(f"  ... and {len(truly_unknown) - 15} more")

# Save
df.to_csv('data/incidents_in_progress.csv', index=False)

# Final stats
remaining_missing = df[df['latitude'].isna() | df['longitude'].isna()]

print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)
print(f"Original count: {original_count}")
print(f"Removed international/unusable: {len(to_remove)}")
print(f"Fixed with default coords: {fixed_count}")
print(f"Final count: {len(df)}")
print(f"With coordinates: {len(df) - len(remaining_missing)}")
print(f"Still missing coordinates: {len(remaining_missing)}")







