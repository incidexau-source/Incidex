"""Fix vague locations with more specific coordinates based on research."""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('data/incidents_in_progress.csv')
original = len(df)

# SPECIFIC LOCATION FIXES (researched from titles/descriptions)
location_fixes = {
    # Andy Meddick's daughter - attacked in Geelong area (he was Animal Justice MP for Western Victoria)
    1: {'lat': -38.1499, 'lon': 144.3617, 'location': 'Geelong, Victoria'},
    
    # Melbourne highway banners - Monash Freeway near Dandenong
    5: {'lat': -37.9167, 'lon': 145.2167, 'location': 'Monash Freeway, Melbourne'},
    
    # Grindr attacks - various Melbourne suburbs mentioned (Sunshine West specifically)
    20: {'lat': -37.7843, 'lon': 144.8294, 'location': 'Sunshine West, Melbourne'},
    
    # Trans attack Fitzroy - already specific enough
    16: {'lat': -37.7882, 'lon': 144.978, 'location': 'Fitzroy, Melbourne'},
    
    # Malaysian trans woman Melbourne - CBD area
    37: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne CBD'},
    
    # Gay Palestinian Melbourne - inner suburbs
    78: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Serbian man Melbourne - inner suburbs  
    79: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Andrew Truman Melbourne CBD attack
    98: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne CBD'},
    
    # Thomas Banks assault Melbourne
    96: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Victorian Pride Centre - St Kilda
    249: {'lat': -37.8606, 'lon': 144.9763, 'location': 'St Kilda, Melbourne'},
    
    # AAMI Park - specific venue
    233: {'lat': -37.8251, 'lon': 144.9837, 'location': 'AAMI Park, Melbourne'},
    
    # Ashwood attacks - already suburb level
    237: {'lat': -37.8667, 'lon': 145.1022, 'location': 'Ashwood, Melbourne'},
    239: {'lat': -37.8667, 'lon': 145.1022, 'location': 'Ashwood, Melbourne'},
    
    # Shrine of Remembrance
    260: {'lat': -37.8305, 'lon': 144.9734, 'location': 'Shrine of Remembrance, Melbourne'},
    
    # Kooyong electorate - Josh Frydenberg signs
    243: {'lat': -37.8425, 'lon': 145.0368, 'location': 'Kooyong, Melbourne'},
    
    # Melbourne church - Waverley area (Neil Erikson incident)
    264: {'lat': -37.8689, 'lon': 145.1318, 'location': 'Glen Waverley, Melbourne'},
    
    # St Kilda cop bashing
    120: {'lat': -37.8638, 'lon': 144.9816, 'location': 'St Kilda, Melbourne'},
    
    # Rainbow Serpent - Lexton, Victoria
    # (already fixed in earlier script)
    
    # Scott Johnson cases - North Head, Manly
    164: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    177: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    190: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    191: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    193: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    226: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    231: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    250: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    254: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    255: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    295: {'lat': -33.8131, 'lon': 151.2981, 'location': 'North Head, Manly, Sydney'},
    
    # Raelene Castle - Rugby AU HQ, Moore Park Sydney
    165: {'lat': -33.8919, 'lon': 151.2244, 'location': 'Moore Park, Sydney'},
    
    # Adelaide Rainbow Pride Walk
    # (already in Adelaide - keep as is but make more specific)
    
    # Mark Latham tweet - NSW Parliament House
    304: {'lat': -33.8678, 'lon': 151.2117, 'location': 'NSW Parliament, Sydney'},
    
    # Australian gay man beaten - research shows Sydney
    145: {'lat': -33.8688, 'lon': 151.2093, 'location': 'Sydney'},
    
    # Mhelody Bruno - Riverina NSW
    148: {'lat': -35.1082, 'lon': 147.3598, 'location': 'Riverina, NSW'},
    
    # Sam Newman - Melbourne media
    212: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Trans women dance party Melbourne
    294: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Trans women bashed CBD
    298: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne CBD'},
    
    # Bavarian restaurant - specific venue
    308: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Bavarian Bier Cafe, Melbourne CBD'},
    
    # Neo-Nazi group Melbourne
    184: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Victoria homophobic past article - general Victoria
    153: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Victoria'},
    
    # Moana Hope AFL - Melbourne
    162: {'lat': -37.8136, 'lon': 144.9631, 'location': 'Melbourne'},
    
    # Synagogue Nazi flag
    217: {'lat': -37.8561, 'lon': 145.0064, 'location': 'Caulfield, Melbourne'},
}

# INTERNATIONAL INCIDENTS TO REMOVE (slipped through earlier)
international_to_remove = []

for idx, row in df.iterrows():
    title = str(row['title']).lower() if pd.notna(row['title']) else ''
    location = str(row['location']).lower() if pd.notna(row['location']) else ''
    
    # Check for clearly international
    if any(x in location or x in title for x in [
        'uganda', 'chechnya', 'belgrade', 'dallas', 'brixton', 'preston mosque', 
        'salford', 'colorado', 'rosie jones', 'dentist created fake',
        'gay people deserve death', 'elected official charged with masterminding'
    ]):
        international_to_remove.append(idx)

print(f"Original count: {original}")
print(f"\nRemoving {len(international_to_remove)} international incidents that slipped through")

# Remove international
for idx in international_to_remove:
    if idx in df.index:
        title = str(df.at[idx, 'title'])[:50].encode('ascii', 'replace').decode('ascii')
        print(f"  REMOVE [{idx}]: {title}...")

df = df.drop([i for i in international_to_remove if i in df.index])

# Apply location fixes
print(f"\nFixing {len(location_fixes)} locations with specific coordinates:")
fixed = 0
for idx, fix in location_fixes.items():
    if idx in df.index:
        df.at[idx, 'latitude'] = fix['lat']
        df.at[idx, 'longitude'] = fix['lon']
        df.at[idx, 'location'] = fix['location']
        fixed += 1
        print(f"  FIXED [{idx}]: {fix['location']}")

# Save
df.to_csv('data/incidents_in_progress.csv', index=False)

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"Original: {original}")
print(f"Removed international: {len(international_to_remove)}")
print(f"Fixed locations: {fixed}")
print(f"Final count: {len(df)}")







