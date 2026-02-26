"""Remove non-Australian incidents from the dataset."""
import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

# Row indices to remove (0-indexed, excluding header)
remove_indices = {49, 59, 66, 67, 76, 85, 91, 92, 93, 94, 96, 97, 102, 117, 129, 132, 138, 141, 144, 146, 148, 153, 160, 163, 168, 170, 185}

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

print(f'Total rows before: {len(rows)}')
print(f'Rows to remove: {len(remove_indices)}')

# Show what we're removing
print('\n=== REMOVING ===')
for idx in sorted(remove_indices):
    if idx < len(rows):
        print(f'  Row {idx}: {rows[idx]["location"][:40]} | {rows[idx]["title"][:50]}')

# Keep only Australian incidents
kept = [r for i, r in enumerate(rows) if i not in remove_indices]
print(f'\nTotal rows after: {len(kept)}')

# Write back
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in kept:
        writer.writerow(r)

print('Done. International incidents removed.')
