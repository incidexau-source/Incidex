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

# === DUPLICATES TO REMOVE ===

# 1. Scott Johnson 1988 murder - 25 rows for ONE incident
# Keep row 146 (Advocate.com - detailed, reputable LGBTIQ source)
# Remove all others
scott_johnson_keep = 146
scott_johnson_all = [31, 138, 139, 140, 142, 144, 145, 146, 147, 150, 154, 162, 165, 193, 195, 197, 217, 218, 220, 221, 222, 255, 256, 258, 260]
scott_johnson_remove = [i for i in scott_johnson_all if i != scott_johnson_keep]

# 2. Oxford Street Darlinghurst 2022-01-15 bashing - 3 rows for ONE incident
# Keep row 224 (Green Left - most detailed description)
# Remove 228 and 241
oxford_remove = [228, 241]

# 3. Journo "chaos" rows 109, 110 - not actual LGBTIQ hate crime incidents
# These are about a journalist's question causing controversy - no date, no incident
journo_remove = [109, 110]

# 4. Warringah Katherine Deves 212, 213 - threats against anti-trans politician
# Not LGBTIQ hate crimes (threats were directed AT an anti-trans campaigner)
# These are also duplicates of each other (same Daily Mail, different articles)
warringah_remove = [212, 213]

all_remove = set(scott_johnson_remove + oxford_remove + journo_remove + warringah_remove)

print(f'Rows to remove: {len(all_remove)}')
print()

print('--- Scott Johnson duplicates (keeping row 146 from Advocate.com) ---')
for idx in sorted(scott_johnson_remove):
    print(f'  REMOVE Row {idx}: {rows[idx]["title"][:70]}')
print()

print('--- Oxford St duplicates (keeping row 224) ---')
for idx in oxford_remove:
    print(f'  REMOVE Row {idx}: {rows[idx]["title"][:70]}')
print()

print('--- Non-LGBTIQ-hate-crime rows ---')
for idx in journo_remove + warringah_remove:
    print(f'  REMOVE Row {idx}: {rows[idx]["title"][:70]}')
print()

# Write filtered CSV
kept = [r for i, r in enumerate(rows) if i not in all_remove]
print(f'Total rows after: {len(kept)}')

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in kept:
        writer.writerow(r)

print('Done. CSV updated.')
