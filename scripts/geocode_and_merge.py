"""
Geocode incidents missing coordinates and merge into main dataset.
"""

import time
import sys
import os
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

MAIN_FILE = DATA_DIR / "incidents_in_progress.csv"
QUEER_NEWS_FILE = DATA_DIR / "queer_news_progress.csv"
BACKFILL_FILE = DATA_DIR / "backfill_2015_2019_incidents.csv"
OVERNIGHT_FILE = DATA_DIR / "overnight_search_new_incidents.csv"

geolocator = Nominatim(user_agent="lgbtiq-geocoder-merge")


def geocode_location(location_string: str) -> tuple:
    """Geocode a location string to coordinates."""
    if not location_string or pd.isna(location_string):
        return None, None
    
    # Skip non-Australian or invalid locations
    invalid_terms = ['not specified', 'unknown', 'null', '', 'n/a', 
                     'egypt', 'usa', 'uk', 'london', 'new york', 'poland',
                     'chechnya', 'croatia', 'finland', 'brazil', 'puerto rico',
                     'malaysia', 'wyoming', 'dalston']
    if location_string.lower().strip() in invalid_terms:
        return None, None
    
    # Skip if clearly not Australian
    non_aus_indicators = ['mosque', 'synagogue', 'church', 'settlement']
    if any(ind in location_string.lower() for ind in non_aus_indicators) and 'australia' not in location_string.lower():
        # Try adding Australia anyway for ambiguous cases
        pass
    
    try:
        # Add Australia to improve geocoding
        if 'australia' not in location_string.lower():
            search_query = f"{location_string}, Australia"
        else:
            search_query = location_string
            
        location = geolocator.geocode(search_query, timeout=10)
        if location:
            # Verify it's in Australia (roughly -10 to -45 lat, 110 to 155 lon)
            if -45 <= location.latitude <= -10 and 110 <= location.longitude <= 155:
                return location.latitude, location.longitude
            else:
                print(f"    [SKIP] Not in Australia: {location_string}")
                return None, None
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"    [ERROR] Geocoding error: {e}")
        return None, None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None, None


def geocode_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Geocode all rows missing coordinates."""
    # Ensure columns exist
    if 'latitude' not in df.columns:
        df['latitude'] = None
    if 'longitude' not in df.columns:
        df['longitude'] = None
    
    missing_coords = df[df['latitude'].isna() | (df['latitude'] == '') | (df['latitude'].astype(str) == 'nan')]
    print(f"\nGeocoding {len(missing_coords)} incidents missing coordinates...")
    
    geocoded_count = 0
    for idx in missing_coords.index:
        location = df.at[idx, 'location']
        if pd.isna(location) or not location:
            continue
            
        safe_loc = str(location)[:50].encode('ascii', 'replace').decode('ascii')
        print(f"  [{geocoded_count+1}/{len(missing_coords)}] Geocoding: {safe_loc}...", end=" ")
        
        lat, lon = geocode_location(location)
        
        if lat and lon:
            df.at[idx, 'latitude'] = lat
            df.at[idx, 'longitude'] = lon
            print(f"OK ({lat:.4f}, {lon:.4f})")
            geocoded_count += 1
        else:
            print("SKIP")
        
        time.sleep(1.1)  # Nominatim rate limit
    
    print(f"\nGeocoded {geocoded_count} new locations")
    return df


def merge_incidents():
    """Merge all incident sources into main file."""
    print("=" * 60)
    print("GEOCODE AND MERGE INCIDENTS")
    print("=" * 60)
    
    # Load main file
    if MAIN_FILE.exists():
        main_df = pd.read_csv(MAIN_FILE)
        print(f"\nLoaded main file: {len(main_df)} incidents")
    else:
        main_df = pd.DataFrame()
        print("\nNo main file found, creating new")
    
    existing_urls = set(main_df['url'].values) if 'url' in main_df.columns else set()
    
    sources = [
        ("Queer News", QUEER_NEWS_FILE),
        ("Backfill 2015-2019", BACKFILL_FILE),
        ("Overnight Search", OVERNIGHT_FILE),
    ]
    
    new_incidents = []
    
    for name, filepath in sources:
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                # Filter out duplicates
                unique = df[~df['url'].isin(existing_urls)]
                if len(unique) > 0:
                    print(f"\n{name}: {len(unique)} new incidents (of {len(df)} total)")
                    new_incidents.append(unique)
                    existing_urls.update(unique['url'].values)
                else:
                    print(f"\n{name}: No new incidents (all {len(df)} already in main)")
            except Exception as e:
                print(f"\n{name}: Error loading - {e}")
        else:
            print(f"\n{name}: File not found")
    
    if not new_incidents:
        print("\nNo new incidents to add")
        return
    
    # Combine new incidents
    combined_new = pd.concat(new_incidents, ignore_index=True)
    print(f"\nTotal new incidents to process: {len(combined_new)}")
    
    # Geocode missing coordinates
    combined_new = geocode_dataframe(combined_new)
    
    # Merge with main
    if len(main_df) > 0:
        final_df = pd.concat([main_df, combined_new], ignore_index=True)
    else:
        final_df = combined_new
    
    # Remove duplicates by URL
    final_df = final_df.drop_duplicates(subset=['url'], keep='first')
    
    # Save
    final_df.to_csv(MAIN_FILE, index=False)
    print(f"\n{'=' * 60}")
    print(f"MERGE COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total incidents in main file: {len(final_df)}")
    
    # Count with coordinates
    with_coords = final_df[final_df['latitude'].notna() & (final_df['latitude'] != '')].shape[0]
    print(f"Incidents with coordinates: {with_coords}")
    print(f"Incidents without coordinates: {len(final_df) - with_coords}")
    print(f"\nMap data updated: {MAIN_FILE}")


if __name__ == "__main__":
    merge_incidents()







