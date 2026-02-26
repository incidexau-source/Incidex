"""Second pass deduplication - remove remaining multi-source duplicates."""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for r in reader:
        rows.append(r)

print(f'Total rows before: {len(rows)}')

remove = set()

# --- Scott Johnson 1988 murder: keep row 137 (Advocate.com, most detailed LGBTIQ source) ---
# Remove all other Scott Johnson articles
sj_keep = 137  # "Arrest Made in 1988 Murder of Gay American Chased Off Sydney Cliff" - Advocate
sj_all = [25, 26, 28, 29, 30, 31, 32, 34, 60, 132, 133, 135, 136, 137, 138, 139, 140, 142, 148, 149, 150, 151, 153, 178, 179, 180, 230]
for i in sj_all:
    if i != sj_keep:
        remove.add(i)

# --- Man glassed for holding boyfriend's hand: rows 37, 38 - same incident ---
# Keep 38 (more descriptive title)
remove.add(37)

# --- Chicken shop kiss assault: rows 35, 43 - same incident ---
# Keep 35 (gaystarnews, more personal account)
remove.add(43)

# --- Sydney drought/homophobic letters: rows 45, 46, 47 - same incident ---
# Keep 47 (Star Observer, Australian LGBTIQ source)
remove.add(45)
remove.add(46)

# --- Lismore rainbow crossing vandalised: rows 96, 97, 98 - same incident ---
# Keep 96 (Star Observer)
remove.add(97)
remove.add(98)

# --- Westfield attack gay man + brother: rows 118, 119 - same incident ---
# Keep 118 (PinkNews)
remove.add(119)

# --- Mark Latham homophobic tweet: rows 235, 236 - same incident ---
# Keep 236 (9news Australian source)
remove.add(235)

# --- Trans women bashed Melbourne: rows 229, 231 - same incident ---
# Keep 231 (more detailed)
remove.add(229)

# --- Adelaide Pride Walk vandalised: rows 124, 125 - same incident ---
# Keep 124 (Star Observer)
remove.add(125)

print(f'Rows to remove: {len(remove)}')
for idx in sorted(remove):
    print(f'  REMOVE Row {idx}: {rows[idx]["title"][:70]}')

kept = [r for i, r in enumerate(rows) if i not in remove]
print(f'\nTotal rows after: {len(kept)}')

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in kept:
        writer.writerow(r)

print('Done.')
