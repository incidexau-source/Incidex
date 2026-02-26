import csv

new_incidents = [
    {
        'title': 'Melbourne man slashed with machete in homophobic attack in Preston',
        'url': 'https://qnews.com.au/melbourne-man-slashed-with-machete-in-homophobic-attack/',
        'source_date': '2024-12-06T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-11-30',
        'location': 'Preston, Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Frank Bonnici, 47, was slashed with a machete by teenagers while walking hand-in-hand with his partner near Darebin Creek in Preston. The attackers yelled homophobic slurs before one pulled out a machete and slashed his arm. He faced weeks of rehab and may never regain full use of his arm.',
        'severity': 'high',
        'perpetrator_info': 'Group of teenagers',
        'latitude': '-37.7448',
        'longitude': '145.0135',
    },
    {
        'title': 'Sydney teens luring and robbing gay men in homophobic dating app attacks',
        'url': 'https://www.starobserver.com.au/news/teens-luring-and-robbing-gay-sydney-men-in-homophobic-attacks/234293',
        'source_date': '2024-12-11T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-01-01',
        'location': 'Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': 'Multiple groups of teenagers weaponised dating apps to lure, attack, and rob gay men across Sydney, with more than a dozen homophobic attacks reported. Victims were forced to falsely confess to pedophilia on camera. Footage was posted to TikTok and Instagram as part of a pedo hunting trend. NSW Police established strike forces to investigate.',
        'severity': 'high',
        'perpetrator_info': 'Multiple groups of teenagers, approximately 20 arrested',
        'latitude': '-33.8688',
        'longitude': '151.2093',
    },
    {
        'title': 'Homophobic graffiti on political signs in Newtown and Enmore Sydney',
        'url': 'https://qnews.com.au/homophobic-graffiti-nsw-police-release-person-of-interest-photos/',
        'source_date': '2025-04-15T00:00:00Z',
        'incident_type': 'vandalism',
        'date': '2025-04-01',
        'location': 'Newtown, Sydney, New South Wales',
        'victim_identity': 'general_lgbtiq',
        'description': 'Offensive homophobic graffiti found on multiple political corflutes in Newtown, Enmore and Erskineville. Inner West Police Area Command investigated and released photos of a person of interest.',
        'severity': 'low',
        'perpetrator_info': 'Unknown, person of interest photos released',
        'latitude': '-33.8977',
        'longitude': '151.1791',
    },
    {
        'title': 'Two Sydney men jailed for Grindr robbery spree targeting gay men',
        'url': 'https://www.starobserver.com.au/news/two-men-jailed-for-using-grindr-in-robberies-across-sydney/236829',
        'source_date': '2025-05-20T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-05-19',
        'location': 'Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': 'Andrew Tanswell (41) and George Leilua (37) were sentenced for robbing five men lured via Grindr between May-June 2023, stealing over $22,000. Tanswell received 6 years 8 months, Leilua 6 years 2 months. Victims included men in their 50s-60s. One victim was threatened with a kitchen knife.',
        'severity': 'high',
        'perpetrator_info': 'Andrew Tanswell, 41, and George Leilua, 37',
        'latitude': '-33.8688',
        'longitude': '151.2093',
    },
    {
        'title': 'Victorian man Christian Keryakus sentenced for TikTok-inspired Grindr attacks',
        'url': 'https://qnews.com.au/victorian-man-sentenced-for-homophobic-attacks-via-grindr/',
        'source_date': '2025-06-03T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-06-02',
        'location': 'Craigieburn, Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Christian Keryakus, 19, pleaded guilty to assaulting two men lured via Grindr. He used a photo of a 15-year-old to entrap victims, accused them of pedophilia, and attacked them with accomplices using a cricket bat. Inspired by TikTok vigilante videos. Sentenced to 2.5-year community corrections order with 250 hours unpaid work.',
        'severity': 'high',
        'perpetrator_info': 'Christian Keryakus, 19, with accomplices',
        'latitude': '-37.6001',
        'longitude': '144.9467',
    },
    {
        'title': 'Five Perth teenagers sentenced for homophobic Grindr luring attacks',
        'url': 'https://www.starobserver.com.au/news/five-perth-teenagers-sentenced-over-homophobic-grindr-attacks/237253',
        'source_date': '2025-06-18T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-06-18',
        'location': 'Perth, Western Australia',
        'victim_identity': 'gay',
        'description': 'Five teenage boys sentenced in Perth Childrens Court for luring gay and bisexual men via fake Grindr profiles to parks on 18 September 2024, then ambushing them with knives, machetes, metal bars, pepper spray and tasers. Sentences ranged from 18 months to 2 years 2 months detention. Judge described attacks as planned and premeditated.',
        'severity': 'high',
        'perpetrator_info': 'Five teenage boys aged 16-17',
        'latitude': '-31.9505',
        'longitude': '115.8605',
    },
    {
        'title': 'Homophobic and antisemitic graffiti on The Laird and Eagle Leather in Melbourne',
        'url': 'https://www.starobserver.com.au/news/iconic-melbourne-venue-the-laird-vandalised-with-homophobic-graffiti/237516',
        'source_date': '2025-07-07T00:00:00Z',
        'incident_type': 'vandalism',
        'date': '2025-07-06',
        'location': 'Abbotsford, Melbourne, Victoria',
        'victim_identity': 'general_lgbtiq',
        'description': 'Iconic LGBTIQ+ venues The Laird and Eagle Leather in Abbotsford were targeted with coordinated homophobic and antisemitic graffiti including God Hates Fags, FAG on doors, neo-Nazi Sonnenrad symbols, and Ned Kelly imagery. Same perpetrators also vandalised the Holocaust Museum in Elsternwick. Victoria Police released images of two suspects.',
        'severity': 'medium',
        'perpetrator_info': 'Two male suspects, neo-Nazi linked',
        'latitude': '-37.8025',
        'longitude': '145.0003',
    },
    {
        'title': 'Nazi salute at Connections Nightclub in Perth - woman fined',
        'url': 'https://www.outinperth.com/perth-woman-who-performed-nazi-salute-at-connections-security-spared-jail-term/',
        'source_date': '2025-08-12T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-07-10',
        'location': 'Northbridge, Perth, Western Australia',
        'victim_identity': 'general_lgbtiq',
        'description': 'Theresa Plunkett-Hill, 43, performed a Nazi salute three times and shouted Heil Hitler at a German security guard after being ejected from Connections Nightclub, an iconic LGBTIQ+ venue in Perth. She was fined $1000 and lost her job.',
        'severity': 'low',
        'perpetrator_info': 'Theresa Plunkett-Hill, 43',
        'latitude': '-31.9477',
        'longitude': '115.8575',
    },
    {
        'title': 'Queensland man jailed for Grindr vigilante attack in Cairns',
        'url': 'https://gayexpress.co.nz/2025/07/queensland-man-jailed-after-grindr-vigilante-attack/',
        'source_date': '2025-07-28T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-07-28',
        'location': 'Smithfield, Cairns, Queensland',
        'victim_identity': 'gay',
        'description': 'Blake Nightingall, 20, pleaded guilty to luring a man via fake Grindr profile using photos of himself as a 15-year-old to Smithfield library. Victim was confronted by three people with a baseball bat, beaten, choked, and robbed. Nightingall sentenced to 10 months imprisonment with immediate parole. A GoFundMe fundraiser raised $660 for the attacker before being removed.',
        'severity': 'high',
        'perpetrator_info': 'Blake Nightingall, 20, with two accomplices',
        'latitude': '-16.8384',
        'longitude': '145.7243',
    },
    {
        'title': 'Two more Perth teenagers sentenced for Grindr luring attacks',
        'url': 'https://www.outinperth.com/two-more-teenagers-sent-to-detention-over-perth-grindr-attacks/',
        'source_date': '2025-09-23T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-09-23',
        'location': 'Perth, Western Australia',
        'victim_identity': 'gay',
        'description': 'Two additional Perth teenagers from the same gang sentenced for luring gay and bisexual men via Grindr. The 18-year-old received 14 months detention; the 16-year-old received 6 months for aggravated armed robbery and assault occasioning bodily harm.',
        'severity': 'high',
        'perpetrator_info': 'Two teenagers, aged 16 and 18',
        'latitude': '-31.9505',
        'longitude': '115.8605',
    },
    {
        'title': 'NSW man convicted in landmark transgender hate speech case',
        'url': 'https://qnews.com.au/nsw-man-convicted-of-transgender-hate-speech/',
        'source_date': '2025-11-19T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-11-19',
        'location': 'Sydney, New South Wales',
        'victim_identity': 'transgender',
        'description': 'Thomas Fordham, 27, convicted in first-ever NSW prosecution for gender identity vilification under Section 93Z of the Crimes Act 1900. He pleaded guilty to threatening or inciting violence on grounds of gender identity after making YouTube comments calling for genocide of transgender people. Sentenced to 12-month community correction order.',
        'severity': 'medium',
        'perpetrator_info': 'Thomas Fordham, 27',
        'latitude': '-33.8688',
        'longitude': '151.2093',
    },
    {
        'title': 'Canberra man charged with Nazi salutes and defacing property',
        'url': 'https://www.afp.gov.au/news-centre/media-release/canberra-man-charged-over-allegedly-giving-nazi-salutes-and-defacing',
        'source_date': '2025-12-15T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2025-12-15',
        'location': 'Canberra, Australian Capital Territory',
        'victim_identity': 'general_lgbtiq',
        'description': 'An 18-year-old from Weston was charged with performing Nazi salutes in public, trespassing, and defacing Commonwealth property including sticking propaganda-style stickers on buildings at the Australian National University.',
        'severity': 'low',
        'perpetrator_info': '18-year-old male from Weston',
        'latitude': '-35.2809',
        'longitude': '149.1300',
    },
    {
        'title': 'Melbourne man targeted with homophobic abuse and online hate in Kensington',
        'url': 'https://www.starobserver.com.au/news/melbourne-man-targeted-with-online-hate-after-sharing-homophobic-experience/240390',
        'source_date': '2026-01-06T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2026-01-02',
        'location': 'Kensington, Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Brad Cresswell-Lee, a JOY 94.9 radio newsreader, was verbally abused with homophobic slurs at JJ Holland Park in Kensington. After confronting the man and filming, the perpetrator falsely accused him of inappropriate behaviour. Cresswell-Lee then received a wave of homophobic abuse online after sharing the incident.',
        'severity': 'medium',
        'perpetrator_info': 'Unknown man in his 50s',
        'latitude': '-37.7941',
        'longitude': '144.9260',
    },
]

# Check for duplicates
fieldnames = ['title', 'url', 'source_date', 'incident_type', 'date', 'location', 'victim_identity', 'description', 'severity', 'perpetrator_info', 'latitude', 'longitude', 'year_found', 'found_at', 'search_query']

csv_path = r'C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map\data\incidents_in_progress.csv'

existing_urls = set()
with open(csv_path, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        existing_urls.add(r['url'].strip())

new_only = [i for i in new_incidents if i['url'] not in existing_urls]
print(f'{len(new_only)} new incidents to add (out of {len(new_incidents)})')
for i in new_only:
    print(f"  {i['date']} | {i['title'][:70]}")

# Add missing fields
for incident in new_only:
    for field in fieldnames:
        if field not in incident:
            incident[field] = ''

# Append
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    for incident in new_only:
        writer.writerow(incident)

print('Done - incidents appended.')
