"""Analyze new data for duplicates and international incidents."""
import pandas as pd
import re
from difflib import SequenceMatcher
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')

print("="*80)
print("DATA ANALYSIS REPORT")
print("="*80)
print(f"\nTotal incidents: {len(df)}")
print(f"With coordinates: {df['latitude'].notna().sum()}")
print(f"Without coordinates: {df['latitude'].isna().sum()}")

# ============================================================
# 1. FIND INTERNATIONAL INCIDENTS
# ============================================================
print("\n" + "="*80)
print("INTERNATIONAL INCIDENTS (outside Australia)")
print("="*80)

AU_LAT_MIN, AU_LAT_MAX = -45, -9
AU_LON_MIN, AU_LON_MAX = 112, 155

with_coords = df.dropna(subset=['latitude', 'longitude'])
outside_au = with_coords[
    (with_coords['latitude'] < AU_LAT_MIN) | 
    (with_coords['latitude'] > AU_LAT_MAX) |
    (with_coords['longitude'] < AU_LON_MIN) | 
    (with_coords['longitude'] > AU_LON_MAX)
]

print(f"\nFound {len(outside_au)} incidents outside Australia:\n")
for idx, row in outside_au.iterrows():
    title = str(row['title'])[:60].encode('ascii', 'replace').decode('ascii')
    location = str(row['location'])[:30].encode('ascii', 'replace').decode('ascii')
    print(f"[{idx}] {location}")
    print(f"     {title}...")
    print(f"     Coords: ({row['latitude']:.2f}, {row['longitude']:.2f})")
    print()

# ============================================================
# 2. FIND DUPLICATES
# ============================================================
print("\n" + "="*80)
print("DUPLICATE DETECTION")
print("="*80)

def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def similarity(t1, t2):
    return SequenceMatcher(None, normalize_text(t1), normalize_text(t2)).ratio()

# Group potential duplicates
duplicate_groups = []
checked = set()

for i in range(len(df)):
    if i in checked:
        continue
    
    row_i = df.iloc[i]
    group = [i]
    
    for j in range(i + 1, len(df)):
        if j in checked:
            continue
        
        row_j = df.iloc[j]
        
        # Check title similarity
        title_sim = similarity(row_i['title'], row_j['title'])
        
        if title_sim > 0.7:
            group.append(j)
            checked.add(j)
    
    if len(group) > 1:
        duplicate_groups.append(group)
        checked.add(i)

print(f"\nFound {len(duplicate_groups)} groups of potential duplicates")
print(f"Total duplicate entries: {sum(len(g) - 1 for g in duplicate_groups)}")

# Show duplicate groups
print("\nDUPLICATE GROUPS:")
print("-"*80)
for i, group in enumerate(duplicate_groups[:30], 1):  # Show first 30 groups
    print(f"\nGroup {i} ({len(group)} entries):")
    for idx in group[:5]:  # Show first 5 of each group
        title = str(df.iloc[idx]['title'])[:65].encode('ascii', 'replace').decode('ascii')
        print(f"  [{df.index[idx]}] {title}...")
    if len(group) > 5:
        print(f"  ... and {len(group) - 5} more")

if len(duplicate_groups) > 30:
    print(f"\n... and {len(duplicate_groups) - 30} more duplicate groups")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total incidents: {len(df)}")
print(f"International (to remove): {len(outside_au)}")
print(f"Duplicate groups: {len(duplicate_groups)}")
print(f"Duplicate entries (to remove): {sum(len(g) - 1 for g in duplicate_groups)}")
print(f"Estimated clean count: {len(df) - len(outside_au) - sum(len(g) - 1 for g in duplicate_groups)}")







