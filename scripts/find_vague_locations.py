"""Find incidents with vague/generic geocoding that need more specific locations."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')

# Generic coordinate centroids to detect
GENERIC_COORDS = {
    'Australia (center)': (-25.27, 133.77, 2.0),  # lat, lon, tolerance
    'Australia (alt)': (-24.77, 134.75, 2.0),
    'NSW (center)': (-32.0, 146.5, 2.0),
    'VIC (center)': (-37.0, 144.5, 1.0),
    'QLD (center)': (-22.0, 145.0, 2.0),
    'SA (center)': (-30.5, 136.0, 2.0),
    'WA (center)': (-26.0, 122.0, 2.0),
    'Unknown (center)': (-36.94, 145.93, 0.5),  # Common geocoding default
}

# Also check for very generic location text
GENERIC_LOCATION_TEXT = [
    'australia', 'not specified', 'unknown', 'not mentioned',
    'victoria', 'queensland', 'new south wales', 'nsw', 
    'western australia', 'south australia', 'tasmania',
    'northern territory', 'australian capital territory'
]

vague_incidents = []

for idx, row in df.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    location = str(row['location']).lower() if pd.notna(row['location']) else ''
    
    is_vague = False
    reason = ''
    
    # Check if coordinates match generic centroids
    for name, (clat, clon, tol) in GENERIC_COORDS.items():
        if abs(lat - clat) < tol and abs(lon - clon) < tol:
            is_vague = True
            reason = f'Generic coords: {name}'
            break
    
    # Check if location text is too generic (but only if specific suburb not mentioned)
    if not is_vague:
        loc_lower = location.strip()
        # Check if it's ONLY a generic term (not "Sydney, NSW" which is fine)
        if loc_lower in GENERIC_LOCATION_TEXT or loc_lower == '':
            is_vague = True
            reason = f'Generic location text: "{location}"'
    
    if is_vague:
        vague_incidents.append({
            'index': idx,
            'location': row['location'],
            'title': row['title'],
            'description': row['description'],
            'url': row['url'],
            'lat': lat,
            'lon': lon,
            'reason': reason
        })

print(f"Total incidents: {len(df)}")
print(f"Vague/generic locations found: {len(vague_incidents)}")
print("\n" + "="*100)
print("INCIDENTS NEEDING MORE SPECIFIC LOCATIONS:")
print("="*100)

for i, inc in enumerate(vague_incidents, 1):
    title = str(inc['title'])[:70].encode('ascii', 'replace').decode('ascii')
    location = str(inc['location'])[:40].encode('ascii', 'replace').decode('ascii')
    desc = str(inc['description'])[:100].encode('ascii', 'replace').decode('ascii') if pd.notna(inc['description']) else 'No description'
    url = str(inc['url'])[:80] if pd.notna(inc['url']) else 'No URL'
    
    print(f"\n[{i}] Index: {inc['index']}")
    print(f"    Location: {location}")
    print(f"    Coords: ({inc['lat']:.4f}, {inc['lon']:.4f})")
    print(f"    Reason: {inc['reason']}")
    print(f"    Title: {title}...")
    print(f"    Desc: {desc}...")
    print(f"    URL: {url}...")

print(f"\n\nTotal needing research: {len(vague_incidents)}")







