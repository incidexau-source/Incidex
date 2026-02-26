"""Third pass deduplication."""
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

# Row 24 & 73: Gold Coast transgender assault - same incident, different sources
# Keep 24 (Star Observer "Community Condemns")
remove.add(73)

# Rows 127 & 128: Sikhs attacked Sydney - same incident
# Keep 127
remove.add(128)

# Rows 62 & 129: Mhelody Bruno - vigil and justice system articles about same murder
# Keep 129 (more detailed about the case)
remove.add(62)

# Rows 99 & 100: Die Antwoord homophobic attack - same incident, different languages
# Keep 99 (English)
remove.add(100)

# Rows 185, 186, 187, 188: NSW inquiry articles - 4 articles about same inquiry opening
# These are all about the inquiry itself, not individual incidents
# Keep 185 (CBS News, most authoritative)
remove.add(186)
remove.add(187)
remove.add(188)

# Rows 1 & 66: Andy Meddick/Victorian MP trans daughter attacked - same incident
# Keep 1 (has location)
remove.add(66)

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
