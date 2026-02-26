import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

no_date = [(i, r) for i, r in enumerate(rows) if not r.get('date', '').strip()]

# Group by whether they have source_date
with_source = [(i, r) for i, r in no_date if r.get('source_date', '').strip()]
without_source = [(i, r) for i, r in no_date if not r.get('source_date', '').strip()]

print(f'Missing date: {len(no_date)}')
print(f'  Has source_date: {len(with_source)}')
print(f'  No source_date either: {len(without_source)}')
print()

print('=== HAS SOURCE_DATE (can potentially extract date from it) ===')
for i, r in with_source:
    print(f'Row {i} | source_date={r["source_date"][:20]} | {r["title"][:70]}')
print()

print('=== NO SOURCE_DATE (need to search) ===')
for i, r in without_source:
    print(f'Row {i} | url={r["url"][:80]}')
    print(f'  title: {r["title"][:80]}')
    print()
