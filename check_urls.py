import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

print(f'Total: {len(rows)}')
print()

# Check for non-http URLs, very short URLs, or suspicious patterns
print('=== POTENTIALLY INVALID URLs ===')
count = 0
for i, r in enumerate(rows):
    url = r.get('url', '').strip()
    bad = False
    reason = ''
    if not url:
        bad = True
        reason = 'EMPTY'
    elif not url.startswith('http'):
        bad = True
        reason = 'NOT HTTP'
    elif len(url) < 20:
        bad = True
        reason = 'TOO SHORT'
    elif ' ' in url:
        bad = True
        reason = 'CONTAINS SPACE'

    if bad:
        count += 1
        print(f'Row {i} [{reason}]: url="{url[:80]}"')
        print(f'  title: {r["title"][:80]}')
        print()

if count == 0:
    print('None found - all URLs appear valid.')

# Also check for missing key fields
print()
print('=== ROWS MISSING KEY FIELDS (date, location, description) ===')
for i, r in enumerate(rows):
    missing = []
    if not r.get('date', '').strip():
        missing.append('date')
    if not r.get('location', '').strip():
        missing.append('location')
    if not r.get('description', '').strip():
        missing.append('description')
    if not r.get('incident_type', '').strip():
        missing.append('incident_type')
    if not r.get('severity', '').strip():
        missing.append('severity')
    if missing:
        print(f'Row {i}: missing {", ".join(missing)} | {r["title"][:70]}')
