import csv, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

print(f'Total incidents: {len(rows)}')
print()

# 1. Check exact URL duplicates
url_map = defaultdict(list)
for i, r in enumerate(rows):
    url = r['url'].strip()
    if url:
        url_map[url].append(i)

print('=== EXACT URL DUPLICATES ===')
found_url_dup = False
for url, indices in url_map.items():
    if len(indices) > 1:
        found_url_dup = True
        print(f'\nURL: {url[:100]}')
        for idx in indices:
            print(f'  Row {idx}: {rows[idx]["date"]} | {rows[idx]["title"][:80]}')
if not found_url_dup:
    print('None found.')

# 2. Check same date + similar location (potential duplicates)
print('\n=== SAME DATE INCIDENTS (potential duplicates) ===')
date_map = defaultdict(list)
for i, r in enumerate(rows):
    d = r['date'].strip()
    if d and d != '':
        date_map[d].append(i)

found_date_dup = False
for date, indices in sorted(date_map.items()):
    if len(indices) > 1:
        found_date_dup = True
        print(f'\nDate: {date}')
        for idx in indices:
            loc = rows[idx]['location'][:40]
            print(f'  Row {idx}: {rows[idx]["title"][:75]} | {loc}')
if not found_date_dup:
    print('None found.')

# 3. Check similar titles (fuzzy - same first 30 chars after lowering)
print('\n=== SIMILAR TITLES (first 30 chars match) ===')
title_map = defaultdict(list)
for i, r in enumerate(rows):
    key = r['title'].strip().lower()[:30]
    if key:
        title_map[key].append(i)

found_title_dup = False
for key, indices in title_map.items():
    if len(indices) > 1:
        found_title_dup = True
        print(f'\nTitle prefix: "{key}"')
        for idx in indices:
            print(f'  Row {idx}: {rows[idx]["date"]} | {rows[idx]["url"][:80]}')
if not found_title_dup:
    print('None found.')

# 4. Check same lat/long pairs (potential same-event duplicates)
print('\n=== SAME COORDINATES + SAME DATE ===')
coord_date_map = defaultdict(list)
for i, r in enumerate(rows):
    lat = r.get('latitude', '').strip()
    lon = r.get('longitude', '').strip()
    d = r['date'].strip()
    if lat and lon and d:
        coord_date_map[(lat, lon, d)].append(i)

found_coord_dup = False
for key, indices in coord_date_map.items():
    if len(indices) > 1:
        found_coord_dup = True
        lat, lon, d = key
        print(f'\n({lat}, {lon}) on {d}:')
        for idx in indices:
            print(f'  Row {idx}: {rows[idx]["title"][:80]}')
if not found_coord_dup:
    print('None found.')

print('\n=== SAME EVENT DIFFERENT SOURCES (same date + overlapping location words) ===')
for date, indices in sorted(date_map.items()):
    if len(indices) > 1:
        # Compare each pair
        for a in range(len(indices)):
            for b in range(a+1, len(indices)):
                ia, ib = indices[a], indices[b]
                loc_a = set(rows[ia]['location'].lower().split(', '))
                loc_b = set(rows[ib]['location'].lower().split(', '))
                overlap = loc_a & loc_b
                if overlap - {'australia', ''}:
                    title_a = rows[ia]['title'][:60]
                    title_b = rows[ib]['title'][:60]
                    print(f'\nDate {date}, shared location words: {overlap}')
                    print(f'  Row {ia}: {title_a}')
                    print(f'  Row {ib}: {title_b}')
