"""
Merge Historical Incidents (2005-2019) with Main Incidents Dataset

This script:
1. Loads historical incidents from historical_incidents_2005_2019.csv
2. Transforms them to match the main incidents format
3. Merges with incidents_in_progress.csv
4. Filters out non-Australian incidents
5. Saves merged dataset
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

HISTORICAL_CSV = DATA_DIR / "historical_incidents_2005_2019.csv"
MAIN_CSV = DATA_DIR / "incidents_in_progress.csv"
OUTPUT_CSV = DATA_DIR / "incidents_in_progress.csv"  # Overwrite main file
BACKUP_CSV = DATA_DIR / "incidents_in_progress_backup_merged.csv"

# Australian state keywords for filtering
AUSTRALIAN_KEYWORDS = [
    'australia', 'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'darwin', 'hobart', 'canberra', 'new south wales', 'nsw', 'victoria', 'vic',
    'queensland', 'qld', 'western australia', 'wa', 'south australia', 'sa',
    'tasmania', 'tas', 'northern territory', 'nt', 'australian capital territory', 'act',
    'darlinghurst', 'newtown', 'fitzroy', 'st kilda', 'surry hills', 'paddington',
    'fortitude valley', 'northbridge', 'north adelaide', 'salamanca', 'fannie bay'
]

def is_australian_location(location_str):
    """Check if location appears to be in Australia."""
    if not location_str or pd.isna(location_str):
        return False
    
    location_lower = str(location_str).lower()
    
    # Check for Australian keywords
    for keyword in AUSTRALIAN_KEYWORDS:
        if keyword in location_lower:
            return True
    
    # Check for non-Australian indicators
    non_aus_indicators = [
        'brooklyn', 'new york', 'georgia', 'monsey', 'rockland', 'indonesia',
        'united states', 'usa', 'uk', 'united kingdom', 'london', 'england',
        'new zealand', 'nz', 'auckland', 'wellington'
    ]
    
    for indicator in non_aus_indicators:
        if indicator in location_lower:
            return False
    
    # If has coordinates, check if they're in Australia bounds
    # Australia: lat -43 to -10, lon 113 to 154
    return None  # Unknown - will check coordinates if available

def parse_historical_date(date_str):
    """Parse DD MM YYYY format to YYYYMMDDTHHMMSSZ format."""
    if not date_str or pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    # Try DD MM YYYY format
    match = re.match(r'(\d{2})\s+(\d{2})\s+(\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        try:
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime("%Y%m%dT%H%M%SZ")
        except:
            pass
    
    # Try other formats
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except:
        return None

def estimate_severity(incident_type):
    """Estimate severity based on incident type."""
    if not incident_type:
        return "medium"
    
    incident_type = str(incident_type).lower()
    
    high_severity = {"assault", "sexual_violence", "murder", "threat"}
    medium_severity = {"harassment", "vandalism", "discrimination", "hate_speech"}
    
    if incident_type in high_severity:
        return "high"
    elif incident_type in medium_severity:
        return "medium"
    else:
        return "low"

def transform_historical_incident(row):
    """Transform historical incident to main format."""
    # Check if Australian
    location = str(row.get('location', '') or '')
    is_aus = is_australian_location(location)
    
    # Skip if clearly not Australian
    if is_aus is False:
        return None
    
    # Create title from description if needed
    title = row.get('article_title', '') or row.get('description', '') or 'Historical Incident'
    if len(title) > 200:
        title = title[:197] + "..."
    
    # Parse date
    date_str = parse_historical_date(row.get('date_of_incident', ''))
    source_date = row.get('publication_date', '')
    if source_date and not date_str:
        try:
            dt = pd.to_datetime(source_date)
            date_str = dt.strftime("%Y%m%dT%H%M%SZ")
        except:
            pass
    
    # Get coordinates
    lat = row.get('latitude', '')
    lon = row.get('longitude', '')
    
    # If not Australian by location but has Australian coordinates, keep it
    if is_aus is None and lat and lon:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            # Australia bounds: lat -43 to -10, lon 113 to 154
            if -43 <= lat_f <= -10 and 113 <= lon_f <= 154:
                is_aus = True
            else:
                is_aus = False
        except:
            pass
    
    # Skip if not Australian
    if is_aus is False:
        return None
    
    # Build incident record
    incident = {
        'title': title,
        'url': row.get('source_url', '') or '',
        'source_date': source_date or date_str or '',
        'incident_type': str(row.get('incident_type', 'other')).lower(),
        'date': date_str or '',
        'location': location,
        'victim_identity': str(row.get('victim_identity', 'unknown')).lower(),
        'description': str(row.get('description', '') or ''),
        'severity': estimate_severity(row.get('incident_type', '')),
        'perpetrator_info': str(row.get('perpetrator_info', '') or ''),
        'latitude': lat if lat and str(lat) != 'nan' else '',
        'longitude': lon if lon and str(lon) != 'nan' else '',
    }
    
    return incident

def main():
    print("=" * 70)
    print("MERGE HISTORICAL INCIDENTS WITH MAIN DATASET")
    print("=" * 70)
    
    # Backup main file
    if MAIN_CSV.exists():
        print(f"\n[1] Backing up main incidents file...")
        import shutil
        shutil.copy2(MAIN_CSV, BACKUP_CSV)
        print(f"    Backup saved to: {BACKUP_CSV.name}")
    
    # Load main incidents
    print(f"\n[2] Loading main incidents from {MAIN_CSV.name}...")
    if MAIN_CSV.exists():
        main_df = pd.read_csv(MAIN_CSV)
        print(f"    Loaded {len(main_df)} existing incidents")
    else:
        print("    No existing incidents file found, starting fresh")
        main_df = pd.DataFrame()
    
    # Load historical incidents
    print(f"\n[3] Loading historical incidents from {HISTORICAL_CSV.name}...")
    if not HISTORICAL_CSV.exists():
        print(f"    ERROR: Historical incidents file not found!")
        return
    
    historical_df = pd.read_csv(HISTORICAL_CSV)
    print(f"    Loaded {len(historical_df)} historical incidents")
    
    # Transform historical incidents
    print(f"\n[4] Transforming historical incidents...")
    transformed_incidents = []
    skipped_non_aus = 0
    skipped_no_location = 0
    
    for idx, row in historical_df.iterrows():
        incident = transform_historical_incident(row)
        if incident is None:
            location = str(row.get('location', '') or '')
            if not location or location.lower() in ['not specified', 'unknown']:
                skipped_no_location += 1
            else:
                skipped_non_aus += 1
            continue
        transformed_incidents.append(incident)
    
    print(f"    Transformed {len(transformed_incidents)} incidents")
    print(f"    Skipped {skipped_non_aus} non-Australian incidents")
    print(f"    Skipped {skipped_no_location} incidents with no location")
    
    if not transformed_incidents:
        print("\n    WARNING: No historical incidents were transformed!")
        return
    
    # Create DataFrame from transformed incidents
    historical_transformed_df = pd.DataFrame(transformed_incidents)
    
    # Merge with main incidents
    print(f"\n[5] Merging datasets...")
    
    # Ensure both have same columns
    required_columns = [
        'title', 'url', 'source_date', 'incident_type', 'date', 'location',
        'victim_identity', 'description', 'severity', 'perpetrator_info',
        'latitude', 'longitude'
    ]
    
    # Add missing columns to both
    for col in required_columns:
        if col not in main_df.columns:
            main_df[col] = ''
        if col not in historical_transformed_df.columns:
            historical_transformed_df[col] = ''
    
    # Reorder columns
    main_df = main_df[required_columns]
    historical_transformed_df = historical_transformed_df[required_columns]
    
    # Merge
    merged_df = pd.concat([main_df, historical_transformed_df], ignore_index=True)
    
    # Remove duplicates based on title and location
    print(f"\n[6] Removing duplicates...")
    before_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['title', 'location'], keep='first')
    duplicates_removed = before_dedup - len(merged_df)
    print(f"    Removed {duplicates_removed} duplicate incidents")
    
    # Save merged dataset
    print(f"\n[7] Saving merged dataset...")
    merged_df.to_csv(OUTPUT_CSV, index=False)
    print(f"    Saved {len(merged_df)} total incidents to {OUTPUT_CSV.name}")
    
    # Summary
    print("\n" + "=" * 70)
    print("MERGE COMPLETE")
    print("=" * 70)
    print(f"Original incidents: {len(main_df)}")
    print(f"Historical incidents added: {len(transformed_incidents)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Total incidents in merged file: {len(merged_df)}")
    print(f"\nOutput file: {OUTPUT_CSV}")
    print(f"Backup file: {BACKUP_CSV}")
    print("=" * 70)

if __name__ == "__main__":
    main()


