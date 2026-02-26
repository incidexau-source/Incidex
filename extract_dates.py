"""
For rows missing 'date', extract the incident date.

Strategy:
1. Many source_dates are article publication dates which are close to the incident.
2. For news articles, the incident typically happened 0-7 days before publication.
3. Use source_date as the date field, formatted as YYYY-MM-DD.
4. This is a reasonable approximation - the source_date at minimum tells us
   when the incident was being reported.
"""
import csv, sys, re
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

updated = 0
for i, r in enumerate(rows):
    if r['date'].strip():
        continue

    sd = r.get('source_date', '').strip()
    if not sd:
        continue

    # Parse source_date format: 20200107T153000Z
    try:
        dt = datetime.strptime(sd[:8], '%Y%m%d')
        r['date'] = dt.strftime('%Y-%m-%d')
        updated += 1
    except ValueError:
        # Try ISO format
        try:
            dt = datetime.fromisoformat(sd.replace('Z', '+00:00'))
            r['date'] = dt.strftime('%Y-%m-%d')
            updated += 1
        except ValueError:
            print(f'Row {i}: Could not parse source_date: {sd}')

print(f'Updated {updated} rows with dates from source_date')

# Write back
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

# Verify
remaining = sum(1 for r in rows if not r['date'].strip())
print(f'Remaining rows without date: {remaining}')
print('Done.')
