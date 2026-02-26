import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

rows = []
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Inspect Scott Johnson cluster
sj_rows = [31, 138, 139, 140, 142, 144, 145, 146, 147, 150, 154, 162, 165, 193, 195, 197, 217, 218, 220, 221, 222, 255, 256, 258, 260]
print('=== SCOTT JOHNSON CLUSTER ===')
for idx in sj_rows:
    r = rows[idx]
    print(f'Row {idx}: date={r["date"]} | type={r["incident_type"]} | severity={r["severity"]}')
    print(f'  title: {r["title"][:80]}')
    print(f'  url: {r["url"][:90]}')
    print(f'  desc: {r["description"][:120]}')
    print()

# Inspect Oxford St cluster
print('=== OXFORD ST 2022-01-15 CLUSTER ===')
for idx in [224, 228, 241]:
    r = rows[idx]
    print(f'Row {idx}: date={r["date"]} | type={r["incident_type"]}')
    print(f'  title: {r["title"][:80]}')
    print(f'  url: {r["url"][:90]}')
    print(f'  desc: {r["description"][:150]}')
    print()

# Inspect journo cluster
print('=== JOURNO CLUSTER ===')
for idx in [109, 110]:
    r = rows[idx]
    print(f'Row {idx}: date={r["date"]} | title: {r["title"][:80]}')
    print(f'  url: {r["url"][:90]}')
    print()

# Inspect Warringah cluster
print('=== WARRINGAH CLUSTER ===')
for idx in [212, 213]:
    r = rows[idx]
    print(f'Row {idx}: date={r["date"]} | title: {r["title"][:80]}')
    print(f'  url: {r["url"][:90]}')
    print()
