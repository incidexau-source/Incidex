import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Initialize geocoder
geolocator = Nominatim(user_agent="lgbtiq-hate-crime-map")

def geocode_location(location_string):
    """
    Convert location string to coordinates
    """
    if pd.isna(location_string) or location_string == 'null':
        return None, None
    
    try:
        # Add ", Australia" to improve accuracy
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        else:
            print(f"  [WARNING] Could not geocode: {location_string}")
            return None, None
            
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"  [ERROR] Error geocoding {location_string}: {e}")
        return None, None

print("=" * 60)
print("GEOCODING INCIDENTS")
print("=" * 60)

# Load incidents
df = pd.read_csv('data/incidents_in_progress.csv')
print(f"\nLoaded {len(df)} incidents")

# Check for existing geocoded data
if 'latitude' not in df.columns:
    df['latitude'] = None
    df['longitude'] = None

# Geocode each incident
geocoded_count = 0
failed_count = 0

for idx, row in df.iterrows():
    # Skip if already geocoded
    if pd.notna(row.get('latitude')):
        geocoded_count += 1
        continue
    
    location = row['location']
    print(f"[{idx+1}/{len(df)}] Geocoding: {location}...", end=" ")
    
    lat, lon = geocode_location(location)
    
    if lat and lon:
        df.at[idx, 'latitude'] = lat
        df.at[idx, 'longitude'] = lon
        geocoded_count += 1
        print(f"[OK] ({lat:.4f}, {lon:.4f})")
    else:
        failed_count += 1
        print("[FAILED]")
    
    # Respect rate limit (1 request/second)
    time.sleep(1)
    
    # Save progress every 50 incidents
    if (idx + 1) % 50 == 0:
        df.to_csv('data/incidents_in_progress.csv', index=False)
        print(f"\n  [PROGRESS] Saved: {geocoded_count} geocoded, {failed_count} failed\n")

# Final save
df.to_csv('data/incidents_in_progress.csv', index=False)

print("\n" + "=" * 60)
print(f"GEOCODING COMPLETE!")
print(f"Successfully geocoded: {geocoded_count}/{len(df)} incidents")
print(f"Failed: {failed_count}")
print(f"Saved to: data/incidents_in_progress.csv")
print("=" * 60)