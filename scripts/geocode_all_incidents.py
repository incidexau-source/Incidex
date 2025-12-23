"""
Geocode all incidents that are missing latitude/longitude coordinates.
Uses Nominatim (OpenStreetMap) geocoder with Australia context.
"""

import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re

# Initialize geocoder
geolocator = Nominatim(user_agent="lgbtiq-hate-crime-map-geocoder")

# Manual coordinate mappings for locations that may not geocode well
MANUAL_COORDS = {
    'fitzroy, melbourne': (-37.7882, 144.9780),
    'fitzroy': (-37.7882, 144.9780),
    'newtown, sydney': (-33.8978, 151.1792),
    'newtown': (-33.8978, 151.1792),
    'oxford street, sydney': (-33.8811, 151.2181),
    'oxford street': (-33.8811, 151.2181),
    'darlinghurst': (-33.8778, 151.2197),
    'darlinghurst, sydney': (-33.8778, 151.2197),
    'sydney cbd': (-33.8688, 151.2093),
    'sydney': (-33.8688, 151.2093),
    'melbourne cbd': (-37.8136, 144.9631),
    'melbourne': (-37.8136, 144.9631),
    'melbourne cbd, victoria': (-37.8136, 144.9631),
    'melbourne, victoria': (-37.8136, 144.9631),
    'brisbane': (-27.4698, 153.0251),
    'brisbane cbd': (-27.4698, 153.0251),
    'adelaide': (-34.9285, 138.6007),
    'adelaide cbd': (-34.9285, 138.6007),
    'adelaide cbd, south australia': (-34.9285, 138.6007),
    'perth': (-31.9505, 115.8605),
    'perth, western australia': (-31.9505, 115.8605),
    'gold coast': (-28.0167, 153.4000),
    'gold coast, queensland': (-28.0167, 153.4000),
    'sunshine coast': (-26.6500, 153.0667),
    'grindr meetup in sunshine coast': (-26.6500, 153.0667),
    'canberra': (-35.2809, 149.1300),
    'canberra, act': (-35.2809, 149.1300),
    'victoria': (-37.4713, 144.7852),
    'new south wales': (-33.8688, 151.2093),
    'queensland': (-27.4698, 153.0251),
    'australia': (-25.2744, 133.7751),
    'australia (national impact)': (-25.2744, 133.7751),
    'melbourne highway': (-37.8136, 144.9631),
    'melbourne highway, melbourne': (-37.8136, 144.9631),
    'great southern region': (-34.8837, 117.8051),
    'sunshine west': (-37.7843, 144.8294),
    'sunshine west, melbourne': (-37.7843, 144.8294),
    "victorian man's home in sunshine west": (-37.7843, 144.8294),
    'new south wales civil and administrative tribunal': (-33.8688, 151.2093),
    'parliament house, spring street, melbourne': (-37.8113, 144.9736),
    'parliament house, spring street, melbourne, victoria': (-37.8113, 144.9736),
    'nsw parliament house, macquarie street, sydney': (-33.8677, 151.2130),
    'brisbane square library, brisbane, queensland': (-27.4698, 153.0251),
    'carindale, brisbane, queensland': (-27.5038, 153.0973),
    'goulburn, nsw': (-34.7546, 149.7187),
    'goulburn': (-34.7546, 149.7187),
    'newcastle, nsw': (-32.9283, 151.7817),
    'newcastle': (-32.9283, 151.7817),
    'paddington, sydney, nsw': (-33.8847, 151.2264),
    'paddington, sydney': (-33.8847, 151.2264),
    'paddington': (-33.8847, 151.2264),
    'blue mountains national park, nsw': (-33.7214, 150.3121),
    'blue mountains national park': (-33.7214, 150.3121),
    'blue mountains': (-33.7214, 150.3121),
    'broulee, nsw': (-35.8586, 150.1792),
    'broulee': (-35.8586, 150.1792),
}

def clean_location(location):
    """Clean up location string for better geocoding"""
    if pd.isna(location) or location == '':
        return None
    
    # Convert to lowercase for matching
    loc = str(location).lower().strip()
    
    # Remove common problematic patterns
    loc = re.sub(r'street\+suburb', '', loc)
    loc = re.sub(r'not specified', '', loc)
    loc = re.sub(r'rainbow story time venue,?\s*', '', loc)
    loc = re.sub(r'farm in unspecified location', 'australia', loc)
    loc = loc.strip(', ')
    
    return loc if loc else None

def geocode_location(location_string):
    """
    Geocode a location string, first checking manual mappings,
    then falling back to Nominatim.
    """
    if not location_string:
        return None, None
    
    # Clean the location
    cleaned = clean_location(location_string)
    if not cleaned:
        return None, None
    
    # Check manual mappings first
    if cleaned in MANUAL_COORDS:
        coords = MANUAL_COORDS[cleaned]
        print(f"    [MANUAL] Found: {coords}")
        return coords
    
    # Try geocoding with Australia context
    try:
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        
        if location:
            print(f"    [GEOCODED] {location.latitude:.4f}, {location.longitude:.4f}")
            return location.latitude, location.longitude
        
        # Try without Australia suffix
        location = geolocator.geocode(location_string, timeout=10)
        if location:
            print(f"    [GEOCODED] {location.latitude:.4f}, {location.longitude:.4f}")
            return location.latitude, location.longitude
            
        print(f"    [NOT FOUND]")
        return None, None
        
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"    [ERROR] {e}")
        return None, None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None, None

def main():
    print("=" * 60)
    print("GEOCODING ALL INCIDENTS")
    print("=" * 60)
    
    # Load incidents
    df = pd.read_csv('data/incidents_in_progress.csv')
    print(f"\nLoaded {len(df)} incidents")
    
    # Find incidents missing coordinates
    missing_lat = df['latitude'].isna() | (df['latitude'] == '')
    missing_lon = df['longitude'].isna() | (df['longitude'] == '')
    missing_coords = missing_lat | missing_lon
    
    print(f"Missing coordinates: {missing_coords.sum()}")
    print(f"Already geocoded: {(~missing_coords).sum()}")
    
    if missing_coords.sum() == 0:
        print("\nAll incidents already have coordinates!")
        return
    
    # Geocode missing locations
    print(f"\nGeocoding {missing_coords.sum()} locations...")
    print("-" * 40)
    
    geocoded_count = 0
    failed_count = 0
    
    for idx in df[missing_coords].index:
        location = df.loc[idx, 'location']
        title = str(df.loc[idx, 'title'])[:50]
        
        print(f"\n[{idx}] {title}...")
        print(f"    Location: {location}")
        
        lat, lon = geocode_location(location)
        
        if lat is not None and lon is not None:
            df.loc[idx, 'latitude'] = lat
            df.loc[idx, 'longitude'] = lon
            geocoded_count += 1
        else:
            # Try to assign default Australia coordinates for completely unlocatable
            if pd.isna(location) or 'not specified' in str(location).lower():
                # Default to Australia center for national/unspecified
                df.loc[idx, 'latitude'] = -25.2744
                df.loc[idx, 'longitude'] = 133.7751
                print(f"    [DEFAULT] Using Australia center")
                geocoded_count += 1
            else:
                failed_count += 1
        
        # Rate limit for Nominatim (1 request per second)
        time.sleep(1.1)
    
    # Save updated data
    df.to_csv('data/incidents_in_progress.csv', index=False)
    df.to_csv('data/incidents_extracted.csv', index=False)
    
    # Final stats
    still_missing = df['latitude'].isna().sum()
    
    print(f"\n{'=' * 60}")
    print("GEOCODING COMPLETE!")
    print(f"Successfully geocoded: {geocoded_count}")
    print(f"Failed to geocode: {failed_count}")
    print(f"Still missing coordinates: {still_missing}")
    print(f"Total incidents with coordinates: {len(df) - still_missing}")
    print(f"Saved to: data/incidents_in_progress.csv")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()











