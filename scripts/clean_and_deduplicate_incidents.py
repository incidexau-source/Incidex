"""
Clean and deduplicate incidents:
1. Remove duplicates
2. Remove incidents outside Australia
3. Remove incidents geocoded in Australia but for international incidents
4. Remove incidents not LGBTIQ+ related
5. Analyze new additions in last 24 hours
"""

import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
INCIDENTS_CSV = DATA_DIR / "incidents_in_progress.csv"
BACKUP_CSV = DATA_DIR / "incidents_in_progress_backup_clean.csv"

# Australian state keywords
AUSTRALIAN_KEYWORDS = [
    'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'darwin', 'hobart', 'canberra', 'new south wales', 'nsw', 'victoria', 'vic',
    'queensland', 'qld', 'western australia', 'wa', 'south australia', 'sa',
    'tasmania', 'tas', 'northern territory', 'nt', 'australian capital territory', 'act'
]

# Non-Australian location indicators
NON_AUSTRALIAN_INDICATORS = [
    'united states', 'usa', 'us', 'america', 'new york', 'brooklyn', 'california',
    'united kingdom', 'uk', 'england', 'london', 'scotland', 'wales',
    'new zealand', 'nz', 'auckland', 'wellington',
    'canada', 'toronto', 'vancouver',
    'indonesia', 'jakarta', 'singapore', 'malaysia',
    'europe', 'france', 'germany', 'italy', 'spain'
]

# LGBTIQ+ related keywords
LGBTIQ_KEYWORDS = [
    'gay', 'lesbian', 'bisexual', 'transgender', 'trans', 'queer', 'lgbtiq', 'lgbt', 'lgbti',
    'homosexual', 'homophobic', 'transphobic', 'biphobic',
    'same-sex', 'same sex', 'rainbow', 'pride', 'mardi gras',
    'sexual orientation', 'gender identity', 'gender diverse'
]

def is_in_australia(lat, lon):
    """Check if coordinates are within Australia bounds."""
    if pd.isna(lat) or pd.isna(lon):
        return None
    
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        # Australia bounds: lat -43 to -10, lon 113 to 154
        return -43 <= lat_f <= -10 and 113 <= lon_f <= 154
    except:
        return None

def is_australian_location(location_str):
    """Check if location string indicates Australia."""
    if not location_str or pd.isna(location_str):
        return None
    
    location_lower = str(location_str).lower()
    
    # Check for non-Australian indicators first
    for indicator in NON_AUSTRALIAN_INDICATORS:
        if indicator in location_lower:
            return False
    
    # Check for Australian keywords
    for keyword in AUSTRALIAN_KEYWORDS:
        if keyword in location_lower:
            return True
    
    return None  # Unknown

def is_lgbtiq_related(row):
    """Check if incident is LGBTIQ+ related."""
    text_to_check = f"{row.get('title', '')} {row.get('description', '')} {row.get('victim_identity', '')}".lower()
    
    for keyword in LGBTIQ_KEYWORDS:
        if keyword in text_to_check:
            return True
    
    # Check incident type
    incident_type = str(row.get('incident_type', '')).lower()
    if incident_type in ['assault', 'harassment', 'vandalism', 'hate_speech', 'discrimination']:
        # If it's a hate crime type, likely LGBTIQ+ related if victim_identity suggests it
        victim = str(row.get('victim_identity', '')).lower()
        if any(kw in victim for kw in ['gay', 'lesbian', 'trans', 'queer', 'lgbtiq', 'bisexual']):
            return True
    
    return False

def is_international_incident(row):
    """Check if incident is about international events but geocoded in Australia."""
    text_to_check = f"{row.get('title', '')} {row.get('description', '')}".lower()
    
    # Check for international context
    international_indicators = [
        'indonesia', 'jakarta', 'united states', 'usa', 'uk', 'united kingdom',
        'new zealand', 'nz', 'canada', 'europe', 'asia'
    ]
    
    location = str(row.get('location', '')).lower()
    
    # If location is clearly Australian but text mentions international places
    if any(kw in location for kw in ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'australia']):
        for indicator in international_indicators:
            if indicator in text_to_check and indicator not in location:
                # Likely an international incident incorrectly geocoded
                return True
    
    return False

def find_duplicates(df):
    """Find duplicate incidents based on title and location similarity."""
    duplicates_to_remove = []
    
    for i in range(len(df)):
        if i in duplicates_to_remove:
            continue
        
        title1 = str(df.iloc[i]['title']).lower().strip()
        loc1 = str(df.iloc[i]['location']).lower().strip()
        url1 = str(df.iloc[i].get('url', '')).strip()
        
        for j in range(i + 1, len(df)):
            if j in duplicates_to_remove:
                continue
            
            title2 = str(df.iloc[j]['title']).lower().strip()
            loc2 = str(df.iloc[j]['location']).lower().strip()
            url2 = str(df.iloc[j].get('url', '')).strip()
            
            # Check for duplicates
            # Same URL = duplicate
            if url1 and url2 and url1 == url2:
                duplicates_to_remove.append(j)
                continue
            
            # Very similar title and location = likely duplicate
            if title1 and title2:
                # Simple similarity check
                words1 = set(title1.split())
                words2 = set(title2.split())
                similarity = len(words1 & words2) / max(len(words1), len(words2)) if words1 or words2 else 0
                
                if similarity > 0.7 and loc1 == loc2:
                    duplicates_to_remove.append(j)
    
    return duplicates_to_remove

def main():
    print("=" * 70)
    print("CLEAN AND DEDUPLICATE INCIDENTS")
    print("=" * 70)
    
    # Backup
    df = pd.read_csv(INCIDENTS_CSV)
    df.to_csv(BACKUP_CSV, index=False)
    print(f"\n[1] Backed up to {BACKUP_CSV.name}")
    print(f"    Original count: {len(df)}")
    
    # Analyze new additions in last 24 hours
    print(f"\n[2] Analyzing new additions in last 24 hours...")
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    new_incidents = []
    for idx, row in df.iterrows():
        source_date = row.get('source_date', '')
        if source_date:
            try:
                # Parse YYYYMMDDTHHMMSSZ format
                if len(source_date) >= 8:
                    year = int(source_date[0:4])
                    month = int(source_date[4:6])
                    day = int(source_date[6:8])
                    incident_date = datetime(year, month, day)
                    if incident_date >= yesterday:
                        new_incidents.append(idx)
            except:
                pass
    
    print(f"    Found {len(new_incidents)} incidents added in last 24 hours")
    
    # Remove duplicates
    print(f"\n[3] Finding and removing duplicates...")
    duplicates = find_duplicates(df)
    print(f"    Found {len(duplicates)} duplicate incidents")
    df = df.drop(df.index[duplicates])
    print(f"    After removing duplicates: {len(df)}")
    
    # Remove incidents outside Australia (by location string first, then coordinates)
    print(f"\n[4] Removing incidents outside Australia...")
    
    # First check by location string
    outside_aus_mask = df.apply(lambda row: is_australian_location(row.get('location', '')) is False, axis=1)
    outside_aus_count = outside_aus_mask.sum()
    print(f"    Found {outside_aus_count} incidents with non-Australian locations")
    df = df[~outside_aus_mask]
    
    # Then check by coordinates
    outside_coords = []
    for idx, row in df.iterrows():
        lat = row.get('latitude')
        lon = row.get('longitude')
        if lat and lon and str(lat) != 'nan' and str(lon) != 'nan':
            in_aus = is_in_australia(lat, lon)
            if in_aus is False:
                outside_coords.append(idx)
    
    print(f"    Found {len(outside_coords)} incidents with coordinates outside Australia")
    if outside_coords:
        df = df.drop(df.index[outside_coords])
    print(f"    After removing: {len(df)}")
    
    # Remove international incidents geocoded in Australia
    print(f"\n[5] Removing international incidents incorrectly geocoded in Australia...")
    international_mask = df.apply(lambda row: is_international_incident(row), axis=1)
    international_count = international_mask.sum()
    print(f"    Found {international_count} international incidents")
    df = df[~international_mask]
    print(f"    After removing: {len(df)}")
    
    # Remove non-LGBTIQ+ related incidents
    print(f"\n[6] Removing non-LGBTIQ+ related incidents...")
    non_lgbtiq_mask = df.apply(lambda row: not is_lgbtiq_related(row), axis=1)
    non_lgbtiq_count = non_lgbtiq_mask.sum()
    print(f"    Found {non_lgbtiq_count} non-LGBTIQ+ related incidents")
    df = df[~non_lgbtiq_mask]
    print(f"    After removing: {len(df)}")
    
    # Save cleaned dataset
    print(f"\n[7] Saving cleaned dataset...")
    df.to_csv(INCIDENTS_CSV, index=False)
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANING COMPLETE")
    print("=" * 70)
    print(f"Original incidents: {len(pd.read_csv(BACKUP_CSV))}")
    print(f"Final incidents: {len(df)}")
    print(f"Removed: {len(pd.read_csv(BACKUP_CSV)) - len(df)}")
    print(f"\nRemoved breakdown:")
    print(f"  - Duplicates: {len(duplicates)}")
    print(f"  - Outside Australia (location): {outside_aus_count}")
    print(f"  - Outside Australia (coordinates): {len(outside_coords)}")
    print(f"  - International incidents: {international_count}")
    print(f"  - Non-LGBTIQ+ related: {non_lgbtiq_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()

