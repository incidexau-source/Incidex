"""Normalize incident_type values."""
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

# Normalize incident types
type_mapping = {
    'hate speech': 'hate_speech',
    'violence': 'assault',
    'killing': 'murder',
    'abduction|rape|torture|murder': 'murder',
    'unsolved deaths': 'murder',
    'anti-gay killings': 'murder',
    'hate crime': 'assault',  # generic, default to assault
}

updated = 0
for r in rows:
    old_type = r['incident_type']
    if old_type in type_mapping:
        r['incident_type'] = type_mapping[old_type]
        print(f'"{old_type}" -> "{r["incident_type"]}" | {r["title"][:50]}')
        updated += 1

print(f'\nUpdated {updated} incident types')

# Write back
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print('Done.')
