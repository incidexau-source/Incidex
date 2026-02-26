"""Check which rows likely have incorrect dates (article pub date vs incident date)."""
import csv, sys, re
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Identify rows where title/description mentions a specific different year
# e.g., "1988 murder" reported in 2020
print('=== ROWS WHERE INCIDENT YEAR LIKELY DIFFERS FROM DATE ===')
count = 0
for i, r in enumerate(rows):
    date = r['date']
    title = r['title'].lower()
    desc = r['description'].lower()
    text = title + ' ' + desc

    # Check for historical references - years mentioned in title that differ from date year
    if not date or len(date) < 4:
        continue
    date_year = date[:4]

    # Find year references in title
    year_matches = re.findall(r'\b(19\d{2}|20[012]\d)\b', title)
    for ym in year_matches:
        if ym != date_year and abs(int(ym) - int(date_year)) > 1:
            count += 1
            print(f'Row {i}: date={date} but title mentions {ym}')
            print(f'  {r["title"][:80]}')
            print()
            break

print(f'Total flagged: {count}')

# Also flag non-Australian incidents
print()
print('=== POTENTIALLY NON-AUSTRALIAN INCIDENTS ===')
non_au_keywords = ['london', 'ukraine', 'united kingdom', 'south africa', 'afghanistan',
                   'iraq', 'malaysia', 'egypt', 'brunei', 'serbia', 'belfast', 'brooklyn',
                   'palestine', 'nashville', 'colorado springs', 'leicester']
for i, r in enumerate(rows):
    loc = r.get('location', '').lower()
    title = r['title'].lower()
    for kw in non_au_keywords:
        if kw in loc or kw in title:
            print(f'Row {i}: {r["title"][:70]} | loc={r["location"][:40]}')
            break
