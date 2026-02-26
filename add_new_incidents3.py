import csv

new_incidents = [
    {
        'title': 'Swastikas and homophobic graffiti on Imperial Hotel and across Inner West Sydney',
        'url': 'https://www.starobserver.com.au/news/swastikas-homophobic-graffiti-found-across-inner-west-on-lgbtq-bar/236423',
        'source_date': '2025-04-09T00:00:00Z',
        'incident_type': 'vandalism',
        'date': '2025-04-08',
        'location': 'Newtown, Enmore, Erskineville, Sydney, New South Wales',
        'victim_identity': 'general_lgbtiq',
        'description': 'Swastikas, homophobic slurs, and offensive graffiti were spray-painted across Newtown, Enmore, and Erskineville between 1:30am-2am, targeting 27 political posters, public structures, and the Imperial Hotel in Erskineville where a swastika was painted over signage reading proudly LGBTQIA+. Felix Kiera, 21, was later charged with 53 offences including 21 counts of displaying a Nazi symbol. He was refused bail.',
        'severity': 'medium',
        'perpetrator_info': 'Felix Kiera, 21, charged with 53 offences',
        'latitude': '-33.8977',
        'longitude': '151.1791',
    },
    {
        'title': 'Man dressed as furry attacked in Rundle Mall Adelaide',
        'url': 'https://www.starobserver.com.au/news/man-dressed-as-a-furry-violently-attacked-in-the-street-in-adelaide/236621',
        'source_date': '2025-05-06T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-05-03',
        'location': 'Rundle Mall, Adelaide, South Australia',
        'victim_identity': 'general_lgbtiq',
        'description': 'Dennis Gunn, 21, was standing in Rundle Mall dressed as a furry holding a Vote 1 Furry Party sign when three men attacked him unprovoked. One launched a flying kick at his head while the others punched him. He was called a paedophile. The attackers targeted him after he high-fived a child while in costume. Police are investigating.',
        'severity': 'medium',
        'perpetrator_info': 'Three unknown men',
        'latitude': '-34.9227',
        'longitude': '138.6023',
    },
    {
        'title': 'Anti-trans activist Kirralie Smith ordered to pay $95k for vilifying trans women',
        'url': 'https://www.starobserver.com.au/news/anti-trans-activist-kirralie-smith-ordered-to-pay-almost-100k-issue-public-apology-following-vilification-ruling/239923',
        'source_date': '2025-12-01T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-12-01',
        'location': 'New South Wales',
        'victim_identity': 'transgender',
        'description': 'Kirralie Smith and Binary Australia were found to have unlawfully vilified two trans women football players through social media posts from 2022-2024, including publishing their photos, names, and locations. First person found to have vilified someone for being trans under NSW law. Ordered to pay $95,000 and issue public apology. Smith is appealing.',
        'severity': 'medium',
        'perpetrator_info': 'Kirralie Smith and Binary Australia',
        'latitude': '-33.8688',
        'longitude': '151.2093',
    },
    {
        'title': 'Amazing Race Australia contestants disqualified over homophobic incident',
        'url': 'https://www.starobserver.com.au/news/luke-and-sassy-scott-break-silence-on-alleged-homophobic-incident-on-the-amazing-race-australia/238588',
        'source_date': '2025-09-15T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-09-09',
        'location': 'Nepal (Australian TV production)',
        'victim_identity': 'gay',
        'description': 'TikTok creators Luke and Sassy Scott O Halloran reported that Dan Middleton approached them six times on the first night of filming Amazing Race Australia Celebrity Edition, making remarks and gestures they found homophobic, offensive, intimidatory and disturbing. Co-star Brendan Fevola intervened and issued an ultimatum to producers. Dan and brother Ant Middleton were disqualified by the next morning.',
        'severity': 'low',
        'perpetrator_info': 'Dan Middleton',
        'latitude': '-33.8688',
        'longitude': '151.2093',
    },
    {
        'title': 'Wave of homophobic hate and threats following Perth 2030 Gay Games announcement',
        'url': 'https://www.outinperth.com/concerns-over-rapidly-escalating-online-hate-speech-directed-at-lgbtiqa-communities/',
        'source_date': '2025-11-01T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-10-27',
        'location': 'Perth, Western Australia',
        'victim_identity': 'general_lgbtiq',
        'description': 'Announcement of Perth hosting the 2030 Gay Games was met with a wave of hateful and abusive comments online. Media outlets including OUTinPerth were forced to lock off social media comments and report threats of violence to authorities. Pride WA President Michael Felix confirmed a strong uptick in hateful comments, noting risks to transgender people, First Nations people, and people of colour within the community.',
        'severity': 'medium',
        'perpetrator_info': 'Multiple online users',
        'latitude': '-31.9505',
        'longitude': '115.8605',
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
