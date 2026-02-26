"""Find remaining Scott Johnson duplicates and other issues."""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

print(f'Total: {len(rows)}')

# Find all Scott Johnson related rows
print('\n=== SCOTT JOHNSON RELATED ROWS ===')
sj = []
for i, r in enumerate(rows):
    t = r['title'].lower()
    if 'scott johnson' in t or 'scott white' in t or ('1988' in t and ('gay' in t or 'cliff' in t) and 'american' in t):
        sj.append(i)
        print(f'Row {i}: date={r["date"]} | {r["title"][:75]}')
print(f'Total Scott Johnson rows: {len(sj)}')

# Find rows with date 1988-12-10 (we set many to this)
print('\n=== ALL ROWS DATED 1988-12-10 ===')
for i, r in enumerate(rows):
    if r['date'] == '1988-12-10':
        print(f'Row {i}: {r["title"][:75]}')

# Find duplicate same-date + similar title pairs
print('\n=== ROWS 37/38 (man glassed) ===')
for i in [37, 38]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')

print('\n=== ROWS 43/35 (chicken shop) ===')
for i in [35, 43]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')

print('\n=== ROWS 45/46/47 (drought letters) ===')
for i in [45, 46, 47]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')

print('\n=== ROWS 96/97/98 (rainbow crossing) ===')
for i in [96, 97, 98]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')

print('\n=== ROWS 118/119 (Westfield attack) ===')
for i in [118, 119]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')

print('\n=== ROWS 235/236 (Mark Latham) ===')
for i in [235, 236]:
    print(f'Row {i}: {rows[i]["title"][:80]} | url={rows[i]["url"][:60]}')
