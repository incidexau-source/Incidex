"""Remove international incidents from dataset."""
import pandas as pd

df = pd.read_csv('data/incidents_in_progress.csv')
original = len(df)

# Australia bounding box
AU_LAT_MIN, AU_LAT_MAX = -45, -9
AU_LON_MIN, AU_LON_MAX = 112, 155

def is_in_australia_or_no_coords(row):
    lat, lon = row['latitude'], row['longitude']
    if pd.isna(lat) or pd.isna(lon):
        return True
    return (AU_LAT_MIN <= lat <= AU_LAT_MAX) and (AU_LON_MIN <= lon <= AU_LON_MAX)

df = df[df.apply(is_in_australia_or_no_coords, axis=1)]
df.to_csv('data/incidents_in_progress.csv', index=False)

with_coords = df['latitude'].notna().sum()
without_coords = df['latitude'].isna().sum()

print(f'Original: {original}')
print(f'After removing international: {len(df)}')
print(f'Removed: {original - len(df)} international incidents')
print(f'With coordinates: {with_coords}')
print(f'Without coordinates: {without_coords}')







