"""Fix the final 4 incidents with non-standard date formats."""
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

print(f'Total rows: {len(rows)}')

# Fix specific dates
fixes = {
    123: '1990-01-01',    # Bondi Badlands 1987-1993 - use midpoint
    125: '1988-12-10',    # Scott Johnson "1980s" - known date Dec 10, 1988
    158: '2014-01-01',    # 2014 reinvestigation - use start of year
    159: '2023-06-01',    # Nathan Wilson "not specified" - use article source_date year
}

updated = 0
for idx, new_date in fixes.items():
    if idx < len(rows):
        old = rows[idx]['date']
        rows[idx]['date'] = new_date
        print(f'Row {idx}: "{old}" -> "{new_date}" | {rows[idx]["title"][:50]}')
        updated += 1

print(f'\nUpdated {updated} dates')

# Write back
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print('Done.')
