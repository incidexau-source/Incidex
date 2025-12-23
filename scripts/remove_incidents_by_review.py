"""
Remove incidents based on manual review decisions.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
INCIDENTS_CSV = DATA_DIR / "incidents_in_progress.csv"
BACKUP_CSV = DATA_DIR / "incidents_in_progress_backup_pre_removal.csv"

# Incidents to remove by exact title match
TITLES_TO_REMOVE = [
    "Melbourne Neo - Nazis Target Drag Performer At Family - Friendly Youth Fest",
    "Miss Universe Australia Maria Thattil says men spat at her brother after Mardi Gras in Sydney",
    "Community in mourning after sistergirl stabbed to death",
    "Rainbow walk in Adelaide , Australia vandalised with Jesus loves you graffiti",
    "Man found guilty twice of gay panic murder wins right to appeal fresh conviction",
    "Mark Latham Investigated By NSW Police Over Vile Alex Greenwich Tweet",
    "Perth Grindr scheme - multiple victims robbed and assaulted",
    "Perth Grindr attack - victim tasered and teeth knocked out",
    "Out Gay Australian MP Tim Wilson House Attacked By Vandals",
    "Court finds Anti - trans campaigner Kirralie Smith unlawfully vilified two trans women"
]

# Keywords to identify Scott Johnson / 1988 murder duplicates
SCOTT_JOHNSON_KEYWORDS = [
    "scott johnson",
    "johnson murder",
    "1988 murder",
    "north head",
    "manly cliff",
    "scott johnson case"
]

# Non-Australian location keywords
NON_AUSTRALIAN_LOCATIONS = [
    "afghanistan", "afghan",
    "edinburgh", "scotland",
    "dhaka", "bangladesh",
    "iraq", "baghdad",
    "south africa", "capetown", "cape town",
    "belfast", "northern ireland",
    "egypt", "cairo",
    "brunei", "brunei darussalam"
]

def normalize_text(text):
    """Normalize text for comparison."""
    if pd.isna(text):
        return ""
    return str(text).lower().strip()

def remove_incidents():
    """Remove incidents based on review criteria."""
    print("=" * 70)
    print("REMOVING INCIDENTS BASED ON MANUAL REVIEW")
    print("=" * 70)
    
    # Load dataset
    df = pd.read_csv(INCIDENTS_CSV)
    print(f"\nLoaded {len(df)} incidents")
    
    # Backup
    df.to_csv(BACKUP_CSV, index=False)
    print(f"Backup saved to: {BACKUP_CSV.name}")
    
    removed_indices = []
    removal_reasons = {}
    
    # 1. Remove specific titles
    print(f"\n[1] Removing specific incidents by title...")
    for title in TITLES_TO_REMOVE:
        mask = df['title'].str.contains(title, case=False, na=False, regex=False)
        indices = df[mask].index.tolist()
        if indices:
            for idx in indices:
                removed_indices.append(idx)
                removal_reasons[idx] = f"Specific title removal: {title[:50]}"
            print(f"    Removed '{title[:60]}...' ({len(indices)} incident(s))")
        else:
            print(f"    Not found: '{title[:60]}...'")
    
    # 2. Remove Scott Johnson / 1988 murder duplicates
    print(f"\n[2] Removing Scott Johnson / 1988 murder duplicates...")
    scott_johnson_count = 0
    for idx, row in df.iterrows():
        if idx in removed_indices:
            continue
        
        text = f"{normalize_text(row.get('title', ''))} {normalize_text(row.get('description', ''))} {normalize_text(row.get('location', ''))}"
        
        # Check for Scott Johnson keywords
        if any(keyword in text for keyword in SCOTT_JOHNSON_KEYWORDS):
            removed_indices.append(idx)
            removal_reasons[idx] = "Scott Johnson / 1988 murder duplicate"
            scott_johnson_count += 1
    
    print(f"    Removed {scott_johnson_count} Scott Johnson / 1988 murder incidents")
    
    # 3. Remove incidents outside Australia
    print(f"\n[3] Removing incidents located outside Australia...")
    non_aus_count = 0
    for idx, row in df.iterrows():
        if idx in removed_indices:
            continue
        
        location = normalize_text(row.get('location', ''))
        description = normalize_text(row.get('description', ''))
        title = normalize_text(row.get('title', ''))
        
        # Check location, description, and title for non-Australian locations
        text_to_check = f"{location} {description} {title}"
        
        for location_keyword in NON_AUSTRALIAN_LOCATIONS:
            if location_keyword in text_to_check:
                removed_indices.append(idx)
                removal_reasons[idx] = f"Non-Australian location: {location_keyword}"
                non_aus_count += 1
                break
    
    print(f"    Removed {non_aus_count} incidents outside Australia")
    
    # Remove all identified incidents
    print(f"\n[4] Removing {len(removed_indices)} total incidents...")
    df_cleaned = df.drop(df.index[removed_indices])
    
    # Save cleaned dataset
    df_cleaned.to_csv(INCIDENTS_CSV, index=False)
    
    # Summary
    print("\n" + "=" * 70)
    print("REMOVAL COMPLETE")
    print("=" * 70)
    print(f"Original incidents: {len(df)}")
    print(f"Removed: {len(removed_indices)}")
    print(f"Remaining: {len(df_cleaned)}")
    print(f"\nRemoval breakdown:")
    print(f"  - Specific titles: {len([r for r in removal_reasons.values() if 'Specific title' in r])}")
    print(f"  - Scott Johnson / 1988: {scott_johnson_count}")
    print(f"  - Non-Australian locations: {non_aus_count}")
    print(f"\nCleaned dataset saved to: {INCIDENTS_CSV}")
    print(f"Backup saved to: {BACKUP_CSV}")
    print("=" * 70)
    
    # Create removal log
    removal_log = []
    for idx in removed_indices:
        row = df.loc[idx]
        removal_log.append({
            "index": int(idx),
            "title": row.get('title', ''),
            "location": row.get('location', ''),
            "url": row.get('url', ''),
            "reason": removal_reasons.get(idx, 'Unknown')
        })
    
    log_df = pd.DataFrame(removal_log)
    log_file = DATA_DIR / f"removal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_df.to_csv(log_file, index=False)
    print(f"\nRemoval log saved to: {log_file.name}")
    
    return df_cleaned

if __name__ == "__main__":
    remove_incidents()


