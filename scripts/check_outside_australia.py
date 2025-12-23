"""Check for incidents outside Australia."""
import pandas as pd

df = pd.read_csv('data/incidents_in_progress.csv')

# Australia's approximate bounding box
AU_LAT_MIN, AU_LAT_MAX = -45, -9
AU_LON_MIN, AU_LON_MAX = 112, 155

# Filter incidents with coordinates
with_coords = df.dropna(subset=['latitude', 'longitude'])

# Find incidents outside Australia
outside_au = with_coords[
    (with_coords['latitude'] < AU_LAT_MIN) | 
    (with_coords['latitude'] > AU_LAT_MAX) |
    (with_coords['longitude'] < AU_LON_MIN) | 
    (with_coords['longitude'] > AU_LON_MAX)
]

print(f"Total incidents: {len(df)}")
print(f"With coordinates: {len(with_coords)}")
print(f"Outside Australia: {len(outside_au)}")
print(f"\n{'='*80}")
print("INCIDENTS OUTSIDE AUSTRALIA:")
print('='*80)

for idx, row in outside_au.iterrows():
    print(f"\nLocation: {row['location']}")
    title = str(row['title'])[:75]
    print(f"Title: {title}...")
    print(f"Coords: ({row['latitude']}, {row['longitude']})")
    print(f"Type: {row['incident_type']}")
    print("-" * 40)







