"""Final cleanup of remaining vague locations."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original = len(df)

# REMOVE - International incidents that slipped through
to_remove = [
    49,   # Lebanese belly dancer - international
    60,   # Greens leader NZ - New Zealand
    65,   # Acid attack US citizen - USA
    84,   # Two men hospitalised - UK
]

# REMOVE - Not actually incidents (news commentary, inquiries, general articles)
not_incidents = [
    6,    # Society Insider - news roundup, not incident
    51,   # Letters blame gays for drought - hate speech but location unknown
    94,   # Christian realtor hate speech - location unknown
    115,  # Australian gay bashing DNA advances - general article
    123,  # Billy Vunipola defends post - UK player, opinion piece
    267,  # Australian inquiry - general article about inquiry
]

# FIX - More specific locations based on research
location_fixes = {
    # Steven Anderson - banned from Australia, incident is about his statements
    0: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Australia-wide (banned speaker)'},
    
    # Victoria Grindr attacks - Melbourne area
    17: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne area, Victoria'},
    
    # QLD couple threatening letters - location in article is Sunshine Coast
    59: {'lat': -26.6500, 'lon': 153.0667, 'location': 'Sunshine Coast, Queensland'},
    
    # Queensland transgender assault - Gold Coast based on article
    96: {'lat': -28.0167, 'lon': 153.4000, 'location': 'Gold Coast, Queensland'},
    
    # George Pell - Melbourne Cathedral
    112: {'lat': -37.8102, 'lon': 144.9762, 'location': "St Patrick's Cathedral, Melbourne"},
    
    # Victoria homophobic past article - Melbourne focus
    141: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne, Victoria'},
    
    # Gay panic murder SA - Adelaide
    173: {'lat': -34.9281, 'lon': 138.5999, 'location': 'Adelaide, South Australia'},
    
    # Far-right attack WA - Perth area
    187: {'lat': -31.9505, 'lon': 115.8605, 'location': 'Perth, Western Australia'},
    
    # Gay man house painted rainbow - Tasmania (Hobart)
    195: {'lat': -42.8821, 'lon': 147.3272, 'location': 'Hobart, Tasmania'},
    
    # Men pretend gay to rape - Sydney
    202: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney, NSW'},
    
    # Indian deported assault Sikhs - Harris Park Sydney
    206: {'lat': -33.8167, 'lon': 151.0167, 'location': 'Harris Park, Sydney'},
    
    # Indigenous teenager WA - Geraldton area
    259: {'lat': -28.7780, 'lon': 114.6144, 'location': 'Geraldton, Western Australia'},
    
    # NSW inquiry articles - Sydney (where hearings held)
    265: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney, NSW (inquiry)'},
    266: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney, NSW (inquiry)'},
    270: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney, NSW (inquiry)'},
    272: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney, NSW (inquiry)'},
    
    # Antisemitism graves - Rookwood Cemetery Sydney
    285: {'lat': -33.8762, 'lon': 151.0539, 'location': 'Rookwood Cemetery, Sydney'},
}

# Remove
all_remove = to_remove + not_incidents
print(f"Removing {len(all_remove)} international/non-incidents:")
for idx in all_remove:
    if idx in df.index:
        title = str(df.at[idx, 'title'])[:50].encode('ascii', 'replace').decode('ascii')
        print(f"  REMOVE [{idx}]: {title}...")

df = df.drop([i for i in all_remove if i in df.index])

# Fix locations
print(f"\nFixing {len(location_fixes)} locations:")
fixed = 0
for idx, fix in location_fixes.items():
    if idx in df.index:
        df.at[idx, 'latitude'] = fix['lat']
        df.at[idx, 'longitude'] = fix['lon']
        df.at[idx, 'location'] = fix['location']
        fixed += 1
        print(f"  FIXED [{idx}]: {fix['location']}")

df.to_csv('data/incidents_in_progress.csv', index=False)

print(f"\n{'='*60}")
print("FINAL SUMMARY")
print(f"{'='*60}")
print(f"Original: {original}")
print(f"Removed: {len(all_remove)}")
print(f"Fixed: {fixed}")
print(f"Final: {len(df)}")







