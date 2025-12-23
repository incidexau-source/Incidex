"""
Geocode incidents missing coordinates by analyzing their URLs/articles.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
INCIDENTS_CSV = DATA_DIR / "incidents_in_progress.csv"

geolocator = Nominatim(user_agent="lgbtiq-hate-crime-map-geocoder")

def extract_location_from_article(url, title, description):
    """Extract location information from article URL."""
    location_hints = []
    
    # Handle NaN values
    if pd.isna(url):
        url = ''
    if pd.isna(title):
        title = ''
    if pd.isna(description):
        description = ''
    
    # Check title and description first
    text_to_check = f"{title} {description}".lower()
    
    # Look for Australian locations in text
    aus_locations = [
        'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'darwin', 'hobart', 'canberra',
        'new south wales', 'nsw', 'victoria', 'vic', 'queensland', 'qld',
        'western australia', 'wa', 'south australia', 'sa', 'tasmania', 'tas',
        'northern territory', 'nt', 'australian capital territory', 'act'
    ]
    
    for loc in aus_locations:
        if loc in text_to_check:
            location_hints.append(loc)
    
    # Try to fetch article if URL available
    if url and str(url) != 'nan' and str(url).startswith('http'):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                article_text = soup.get_text().lower()
                
                # Look for location mentions
                for loc in aus_locations:
                    if loc in article_text:
                        location_hints.append(loc)
                
                # Look for specific suburbs/areas
                location_patterns = [
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*(NSW|VIC|QLD|WA|SA|TAS|NT|ACT|Victoria|New South Wales|Queensland|Western Australia|South Australia|Tasmania|Northern Territory)',
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(NSW|VIC|QLD|WA|SA|TAS|NT|ACT)',
                ]
                
                for pattern in location_patterns:
                    matches = re.findall(pattern, article_text)
                    for match in matches:
                        if isinstance(match, tuple):
                            location_hints.append(' '.join(match))
                        else:
                            location_hints.append(match)
        except Exception as e:
            print(f"    Error fetching article: {e}")
    
    return location_hints

def geocode_location(location_string):
    """Geocode a location string."""
    if not location_string:
        return None, None
    
    try:
        # Try with Australia context
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        
        if location:
            # Verify it's in Australia (lat -43 to -10, lon 113 to 154)
            if -43 <= location.latitude <= -10 and 113 <= location.longitude <= 154:
                return location.latitude, location.longitude
        
        # Try without Australia suffix
        location = geolocator.geocode(location_string, timeout=10)
        if location:
            if -43 <= location.latitude <= -10 and 113 <= location.longitude <= 154:
                return location.latitude, location.longitude
        
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"    Geocoding error: {e}")
        return None, None
    except Exception as e:
        print(f"    Error: {e}")
        return None, None

def main():
    print("=" * 70)
    print("GEOCODING MISSING INCIDENTS")
    print("=" * 70)
    
    # Load incidents
    df = pd.read_csv(INCIDENTS_CSV)
    print(f"\nLoaded {len(df)} total incidents")
    
    # Find incidents missing coordinates
    missing_mask = (
        df['latitude'].isna() | 
        (df['latitude'] == '') | 
        df['longitude'].isna() | 
        (df['longitude'] == '')
    )
    missing_df = df[missing_mask].copy()
    
    print(f"Found {len(missing_df)} incidents missing coordinates")
    
    if len(missing_df) == 0:
        print("No incidents need geocoding!")
        return
    
    # Process each missing incident
    geocoded_count = 0
    for i, (idx, row) in enumerate(missing_df.iterrows(), 1):
        title = str(row['title'])[:60] if pd.notna(row['title']) else 'Unknown'
        location = str(row['location']) if pd.notna(row['location']) else ''
        url = str(row['url']) if pd.notna(row['url']) and str(row['url']) != 'nan' else ''
        
        print(f"\n[{i}/{len(missing_df)}] Processing: {title}...")
        print(f"    Current location: {location}")
        print(f"    URL: {url}")
        
        # Try to extract location from article
        location_hints = extract_location_from_article(
            row.get('url', ''),
            row.get('title', ''),
            row.get('description', '')
        )
        
        # Check if location is clearly non-Australian first
        location_str = str(row.get('location', '')).lower()
        non_aus_indicators = ['united states', 'usa', 'us', 'new york', 'brooklyn', 'wisconsin', 
                             'norway', 'oslo', 'chicago', 'bahrain', 'seattle', 'massachusetts',
                             'indonesia', 'toronto', 'poland', 'mongolia', 'taiwan', 'michigan',
                             'florida', 'wales', 'uk', 'united kingdom']
        
        is_non_aus = any(indicator in location_str for indicator in non_aus_indicators)
        
        if is_non_aus:
            print(f"    [SKIP] Non-Australian location detected")
            continue
        
        # Try geocoding with existing location first
        lat, lon = None, None
        if location and location.strip():
            lat, lon = geocode_location(location)
        
        # If that failed, try location hints (but only if they're Australian)
        if not lat or not lon:
            for hint in location_hints[:3]:  # Try first 3 hints
                if hint and hint.lower() in ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 
                                            'darwin', 'hobart', 'canberra', 'nsw', 'vic', 'qld', 
                                            'wa', 'sa', 'tas', 'nt', 'act', 'victoria', 'queensland']:
                    print(f"    Trying hint: {hint}")
                    lat, lon = geocode_location(hint)
                    if lat and lon:
                        # Update location field too
                        df.at[idx, 'location'] = hint
                        break
        
        if lat and lon:
            df.at[idx, 'latitude'] = lat
            df.at[idx, 'longitude'] = lon
            geocoded_count += 1
            print(f"    [OK] Geocoded: {lat:.6f}, {lon:.6f}")
        else:
            print(f"    [FAIL] Could not geocode")
        
        # Rate limiting
        time.sleep(1)
    
    # Save updated dataset
    print(f"\n{'='*70}")
    print(f"GEOCODING COMPLETE")
    print(f"{'='*70}")
    print(f"Geocoded: {geocoded_count}/{len(missing_df)} incidents")
    
    df.to_csv(INCIDENTS_CSV, index=False)
    print(f"\nSaved updated dataset to {INCIDENTS_CSV}")

if __name__ == "__main__":
    main()

