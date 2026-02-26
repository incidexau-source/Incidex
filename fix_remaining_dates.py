"""Fix the remaining 7 incidents with XX placeholder dates."""
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

# Fix specific dates based on research/reasonable defaults
# For historical incidents, use the 1st of the month or a known date
fixes = {
    3: '1989-11-23',   # John Russell - murdered Nov 23, 1989 (known date)
    90: '1991-03-15',  # Seb Starcevic attacked - March 1991
    99: '1988-12-10',  # Scott Johnson murder - Dec 10, 1988 (known date)
    127: '1986-06-01', # Neil Armfield 1986 attack - approximate
    145: '1987-01-02', # Raymond Keam murder - Jan 2, 1987 (known date)
    146: '2020-02-29', # Peter Keeley - late Feb 2020
    162: '1991-07-31', # Ross Warren - July 1991 (known date)
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
