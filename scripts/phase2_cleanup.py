
import os
import sys
import pandas as pd
import logging
import re
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from scripts.config import PHASE1_OUTPUT, CLEANED_OUTPUT, INTL_EXCLUSIONS, CLEANUP_REPORT

# Schema Harmonization
# We want a unified set of columns for the final dataset
FINAL_COLUMNS = [
    "title", "url", "incident_type", "date", "location", 
    "victim_identity", "description", "confidence", "severity", 
    "source_name", "verified", "latitude", "longitude", "perpetrator_info"
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Phase2")

def is_australian(location_str, source_name="") -> bool:
    """Enhanced check for Australian locations with context awareness."""
    if not isinstance(location_str, str) or location_str == "nan": return False
    loc = location_str.lower()
    
    au_sources = ['abc.net.au', 'sbs.com.au', 'starobserver.com.au', 'smh.com.au', 'theage.com.au', 'pinknews']
    is_from_au_source = any(s in source_name.lower() for s in au_sources)

    au_markers = [
        'nsw', 'vic', 'qld', 'wa', 'sa', 'tas', 'act', 'nt', 'australia', 
        'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'darwin', 
        'hobart', 'canberra', 'queensland', 'victoria', 'new south wales', 
        'tasmania', 'gold coast', 'newcastle', 'darlinghurst', 'newtown'
    ]
    
    intl_markers = ['usa', 'uk ', 'united kingdom', 'london', 'new york', 'canada', 'brazil', 'india', 'germany', 'france']
    
    has_intl = any(re.search(r'\b' + re.escape(m) + r'\b', loc) for m in intl_markers)
    has_au = any(re.search(r'\b' + re.escape(m) + r'\b', loc) for m in au_markers)
    
    if has_intl: return False
    if has_au: return True
    if is_from_au_source: return True
    return False

def map_phase1(df):
    """Map Phase 1 columns to unified schema."""
    mapping = {
        "article_title": "title",
        "article_url": "url",
        "date_of_incident": "date",
        "confidence_score": "confidence",
        "source_name": "source_name"
    }
    df = df.rename(columns=mapping)
    # Ensure missing columns exist
    for col in FINAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[FINAL_COLUMNS]

def map_existing(df):
    """Map existing incidents_in_progress.csv columns to unified schema."""
    # Existing headers: title,url,source_date,incident_type,date,location,victim_identity,description,severity,perpetrator_info,latitude,longitude
    if 'confidence_score' in df.columns:
        df = df.rename(columns={'confidence_score': 'confidence'})
    elif 'confidence' not in df.columns:
        df['confidence'] = 70 # Default for historical verified data
    
    if 'source_name' not in df.columns:
        df['source_name'] = "historical_discovery"

    # Map lat/lng to latitude/longitude if needed
    if 'latitude' not in df.columns and 'lat' in df.columns:
        df = df.rename(columns={'lat': 'latitude', 'lng': 'longitude'})
    
    if 'perpetrator_info' not in df.columns:
        df['perpetrator_info'] = ""
    for col in FINAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
            
    return df[FINAL_COLUMNS]

def run_phase2():
    logger.info("Starting Phase 2: Cleanup, Harmonization & Deduplication")
    
    all_dfs = []
    
    # 1. Load Phase 1 Data
    if os.path.exists(PHASE1_OUTPUT):
        try:
            df_p1 = pd.read_csv(PHASE1_OUTPUT)
            if len(df_p1) > 0:
                all_dfs.append(map_phase1(df_p1))
                logger.info(f"Loaded {len(df_p1)} incidents from Phase 1.")
        except Exception as e:
            logger.error(f"Error loading Phase 1: {e}")

    # 2. Load Existing Data
    existing_path = os.path.join(BASE_DIR, "data", "incidents_in_progress.csv")
    if os.path.exists(existing_path):
        try:
            df_ex = pd.read_csv(existing_path)
            if len(df_ex) > 0:
                all_dfs.append(map_existing(df_ex))
                logger.info(f"Loaded {len(df_ex)} incidents from historical progress file.")
        except Exception as e:
            logger.error(f"Error loading existing data: {e}")

    if not all_dfs:
        logger.error("No data found to process.")
        return

    df_total = pd.concat(all_dfs, ignore_index=True)
    initial_count = len(df_total)

    # 3. Location Filtering
    df_total['source_name'] = df_total['source_name'].fillna('')
    df_total['is_au'] = df_total.apply(lambda row: is_australian(str(row['location']), str(row['source_name'])), axis=1)
    
    df_au = df_total[df_total['is_au']].copy()
    df_intl = df_total[~df_total['is_au']].copy()
    
    # 4. Deduplication
    # Normalize for matching
    df_au['date_norm'] = pd.to_datetime(df_au['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df_au['loc_norm'] = df_au['location'].str.lower().str.replace(r'[^a-z0-9 ]', '', regex=True).str.strip()
    df_au['type_norm'] = df_au['incident_type'].str.lower().str.strip()
    
    # Sort by confidence to keep best records
    df_au = df_au.sort_values(by='confidence', ascending=False)
    df_final = df_au.drop_duplicates(subset=['date_norm', 'loc_norm', 'type_norm'], keep='first')
    
    # 5. Save Results
    df_final = df_final.drop(columns=['is_au', 'date_norm', 'loc_norm', 'type_norm'])
    df_final.to_csv(CLEANED_OUTPUT, index=False, encoding='utf-8')
    df_intl.to_csv(INTL_EXCLUSIONS, index=False, encoding='utf-8')
    
    # Audit Report
    report = f"""LGBTIQ+ Hate Crime Data Cleanup Report
======================================
Date: {pd.Timestamp.now()}

- Total records processed: {initial_count}
- International/Irrelevant removed: {len(df_intl)}
- Duplicates removed: {len(df_au) - len(df_final)}
- Final Cleaned Count: {len(df_final)}

Output location: {CLEANED_OUTPUT}
"""
    with open(CLEANUP_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
        
    logger.info(f"Phase 2 Complete. Final set: {len(df_final)}")
    print(report)

if __name__ == "__main__":
    run_phase2()
