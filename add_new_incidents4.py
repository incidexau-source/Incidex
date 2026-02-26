import csv

new_incidents = [
    {
        'title': 'Transgender person assaulted by group of youths on Gold Coast tram',
        'url': 'https://www.starobserver.com.au/news/community-condemns-attack-on-transgender-person-on-the-gold-coast/239547',
        'source_date': '2025-11-04T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-11-01',
        'location': 'Broadbeach, Gold Coast, Queensland',
        'victim_identity': 'transgender',
        'description': 'A 25-year-old transgender person was physically assaulted by a group of youths while travelling on a tram to Broadbeach on Saturday November 1. The group targeted the victim and pulled a sticker from their backpack. Brisbane Pride president James McCarthy expressed outrage. The Gold Coast Pride Collective called it a result of misinformation and vilification campaigns against the trans community.',
        'severity': 'medium',
        'perpetrator_info': 'Group of youths',
        'latitude': '-28.0277',
        'longitude': '153.4300',
    },
]

fieldnames = ['title', 'url', 'source_date', 'incident_type', 'date', 'location', 'victim_identity', 'description', 'severity', 'perpetrator_info', 'latitude', 'longitude', 'year_found', 'found_at', 'search_query']
csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

existing_urls = set()
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        existing_urls.add(r['url'].strip())

new_only = [i for i in new_incidents if i['url'] not in existing_urls]
print(f'{len(new_only)} new incidents to add')
for i in new_only:
    print(f"  {i['date']} | {i['title'][:70]}")

for incident in new_only:
    for field in fieldnames:
        if field not in incident:
            incident[field] = ''

with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    for incident in new_only:
        writer.writerow(incident)

print('Done.')
