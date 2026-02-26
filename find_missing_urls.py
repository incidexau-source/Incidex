import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

print(f'Total: {len(rows)}')
print()
print('=== ROWS WITH MISSING OR EMPTY URLs ===')
count = 0
for i, r in enumerate(rows):
    url = r.get('url', '').strip()
    if not url:
        count += 1
        title = r['title'][:90]
        date = r['date']
        loc = r['location'][:50]
        print(f'Row {i}: date={date} | loc={loc}')
        print(f'  title: {title}')
        print(f'  desc: {r["description"][:150]}')
        print()

print(f'Total missing URLs: {count}')
