import csv

# Check cases for missing coordinates and broken links
f = open('data/landmark_cases.csv', encoding='utf-8')
reader = csv.DictReader(f)
cases = list(reader)
f.close()

print('=' * 60)
print('LANDMARK CASES AUDIT')
print('=' * 60)

print(f'\nTotal cases in CSV: {len(cases)}')

# Check coordinates
print('\n--- COORDINATE CHECK ---')
missing_coords = []
for c in cases:
    lat = c.get('latitude', '').strip()
    lon = c.get('longitude', '').strip()
    if not lat or not lon:
        missing_coords.append(c['case_name'])
        print(f"[X] Missing coords: {c['case_name']}")

if not missing_coords:
    print("[OK] All cases have coordinates")
else:
    print(f"\n[!] {len(missing_coords)} cases missing coordinates")

print(f"\nCases with valid coordinates: {len(cases) - len(missing_coords)}")

# List all cases with their coordinates
print('\n--- ALL CASES WITH COORDINATES ---')
for i, c in enumerate(cases, 1):
    lat = c.get('latitude', '').strip()
    lon = c.get('longitude', '').strip()
    status = '[OK]' if lat and lon else '[X]'
    print(f"{i}. {status} {c['case_name']} ({c['year_decided']}) - {c['location']} [{lat}, {lon}]")

# Check links (just list them for manual review)
print('\n--- JUDGMENT LINKS ---')
for c in cases:
    url = c.get('judgment_url', '').strip()
    if url:
        print(f"- {c['case_name']}: {url}")
    else:
        print(f"[X] {c['case_name']}: NO URL")

