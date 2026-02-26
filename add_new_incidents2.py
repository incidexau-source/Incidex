import csv

new_incidents = [
    {
        'title': 'Same-sex couple brutally bashed in homophobic attack in Rundle Mall Adelaide',
        'url': 'https://www.starobserver.com.au/news/south-australian-police-release-footage-of-alleged-homophobic-attackers/234048',
        'source_date': '2024-11-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-11-10',
        'location': 'Rundle Mall, Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': 'Two men in their 20s were holding hands when attacked by two teenagers in Rundle Mall at 8:30pm. One attacker pulled a balaclava over his face before launching the assault while hurling homophobic abuse. One victim was hospitalised with his jaw broken twice; the other sustained significant bruising. Both suspects were arrested and bailed to Adelaide Youth Court.',
        'severity': 'high',
        'perpetrator_info': 'Two teenage boys, both arrested',
        'latitude': '-34.9227',
        'longitude': '138.6023',
    },
    {
        'title': 'NRL star Reece Walsh subjected to homophobic abuse over nail polish in England',
        'url': 'https://www.starobserver.com.au/artsentertainment/reece-walsh-cops-homophobic-abuse-over-nail-polish-in-the-uk/239550',
        'source_date': '2025-11-04T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-11-01',
        'location': 'Liverpool, England (Australian athlete)',
        'victim_identity': 'general_lgbtiq',
        'description': 'Brisbane Broncos fullback Reece Walsh was subjected to homophobic slurs and abuse from English spectators during the 2025 Kangaroos tour match in Liverpool after being sin-binned. Fans mocked him for wearing nail polish, which he credits to his four-year-old daughter.',
        'severity': 'low',
        'perpetrator_info': 'English rugby league spectators',
        'latitude': '53.4084',
        'longitude': '-2.9916',
    },
    {
        'title': 'Burnie councillor suspended for homophobic and racist social media posts',
        'url': 'https://qnews.com.au/burnie-councillor-suspended-for-homophobic-racist-social-posts/',
        'source_date': '2026-01-27T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2026-01-27',
        'location': 'Burnie, Tasmania',
        'victim_identity': 'general_lgbtiq',
        'description': 'Burnie City Councillor Trent Aitken suspended for two weeks after a Code of Conduct Panel found seven homophobic statements in his social media posts made between January-May 2025, including posts criticising transgender people and opposing rainbow flags at council. He was the sole vote against an LGBTQIA+ action plan.',
        'severity': 'low',
        'perpetrator_info': 'Councillor Trent Aitken',
        'latitude': '-41.0511',
        'longitude': '145.9069',
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
