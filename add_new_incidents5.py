import csv

new_incidents = [
    {
        'title': 'Ken Doig murdered at gay beat in Toowoomba on Christmas Eve',
        'url': 'https://www.sbs.com.au/voices/creative/out-of-sight-the-untold-story-of-adelaides-gay-hate-murders/vw9etx2cw',
        'source_date': '2019-01-01T00:00:00Z',
        'incident_type': 'murder',
        'date': '2001-12-24',
        'location': 'Toowoomba, Queensland',
        'victim_identity': 'gay',
        'description': 'Ken Doig was on his way to meet his parents for Midnight Mass on Christmas Eve 2001 when he stopped at a public toilet near Toowoomba, a known gay beat. He was bashed, hit in the head with an axe, and had his throat cut. The murder remains unsolved.',
        'severity': 'high',
        'perpetrator_info': 'Unknown',
        'latitude': '-27.5598',
        'longitude': '151.9507',
    },
    {
        'title': 'Robert Woodland found dead near Adelaide gay beat in suspected hate crime',
        'url': 'https://www.sbs.com.au/voices/creative/out-of-sight-the-untold-story-of-adelaides-gay-hate-murders/vw9etx2cw',
        'source_date': '2019-01-01T00:00:00Z',
        'incident_type': 'murder',
        'date': '2004-12-08',
        'location': 'Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': "Robert Woodland's body was discovered on December 8, 2004. His car was parked in the Veale Gardens car park, while the 36-year-old's corpse was found 700 metres away. He was last seen at the beat at 1am on December 5, after having left a nightclub. Police declared robbery as the motive despite his missing wallet and vicious injuries to his head at a place where gay men were routinely bashed. The murder remains unsolved.",
        'severity': 'high',
        'perpetrator_info': 'Unknown',
        'latitude': '-34.9335',
        'longitude': '138.5986',
    },
    {
        'title': 'Craig Gee brutally bashed in homophobic attack while holding boyfriend hand in Surry Hills',
        'url': 'https://www.starobserver.com.au/news/national-news/new-south-wales-news/police-close-file-on-craig-and-shane-bashing/3202',
        'source_date': '2008-12-03T00:00:00Z',
        'incident_type': 'assault',
        'date': '2007-12-03',
        'location': 'Surry Hills, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': "Craig Gee was attacked by four men while holding his boyfriend Shane Brennen's hand walking down Crown Street in Surry Hills. Part of his skull was reduced to powder and his leg was broken. His head was stomped several times against the pavement. One of the assailants later used Craig's stolen phone to call his mother saying 'We killed your son.' Despite CCTV evidence, police closed the case without arrests. The incident prompted community vigils and changes at Surry Hills Police.",
        'severity': 'high',
        'perpetrator_info': 'Four unknown men',
        'latitude': '-33.8830',
        'longitude': '151.2118',
    },
    {
        'title': 'Two men attacked by homophobic Donald Trump supporter near Newtown Sydney',
        'url': 'https://www.starobserver.com.au/news/national-news/new-south-wales-news/sydney-donald-trump/154154',
        'source_date': '2016-11-14T00:00:00Z',
        'incident_type': 'assault',
        'date': '2016-11-14',
        'location': 'Newtown, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': "Sam and Andrew were attacked near Newtown while in line at a McDonald's by an intoxicated man who was rambling about Donald Trump winning the election, saying things like 'how white men rule now that Trump has won.' The man physically assaulted them in what they described as a homophobic attack.",
        'severity': 'medium',
        'perpetrator_info': 'Unknown intoxicated man',
        'latitude': '-33.8977',
        'longitude': '151.1791',
    },
    {
        'title': 'Three LGBTI people assaulted in transphobic attack in Footscray Melbourne',
        'url': 'https://www.starobserver.com.au/news/national-news/victoria-news/lgbti-assault-melbourne-police/153761',
        'source_date': '2016-11-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2016-11-01',
        'location': 'Footscray, Melbourne, Victoria',
        'victim_identity': 'transgender',
        'description': "Starlady, Canon (a trans man), and Azja were leaving a restaurant in Footscray when a man yelled 'get the fuck out' before chasing them with two friends. One grabbed Azja in a headlock, and when Canon tried to call police, he was punched in the face. Police refused to label the incident a hate crime despite the victims saying it was clearly motivated by prejudice against their gender identity.",
        'severity': 'medium',
        'perpetrator_info': 'Three unknown men',
        'latitude': '-37.8000',
        'longitude': '144.8997',
    },
    {
        'title': 'Sydney drag queens rescue man from homophobic attack on Oxford Street',
        'url': 'https://www.starobserver.com.au/news/national-news/new-south-wales-news/sydney-drag-queens-save-man-homophobic-attack/161084',
        'source_date': '2017-03-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2017-03-01',
        'location': 'Oxford Street, Surry Hills, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': 'Ivan Flinn of Surry Hills was punched after leaving an Oxford Street bar to get a kebab, when he was harassed by a group of men. Drag queens intervened to rescue him. NSW Police confirmed officers broke up an attack involving up to seven people and were investigating a possible homophobic bias motivation.',
        'severity': 'medium',
        'perpetrator_info': 'Group of up to seven men',
        'latitude': '-33.8795',
        'longitude': '151.2177',
    },
    {
        'title': 'Gay men attacked at Footscray Park beat in Melbourne',
        'url': 'https://www.starobserver.com.au/news/national-news/victoria-news/reports-homophobic-violence-melbourne/154844',
        'source_date': '2017-03-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2017-03-01',
        'location': 'Footscray Park, Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Multiple gay men were subjected to homophobic abuse, threats, and physical violence at Footscray Park in Melbourne, a known cruising area. One man was lured into a secluded area before being assaulted by a large group of men. A candlelight vigil was held at Footscray Park on 23 March 2017 in response.',
        'severity': 'medium',
        'perpetrator_info': 'Groups of men targeting gay beat',
        'latitude': '-37.7998',
        'longitude': '144.8862',
    },
    {
        'title': "Kevin Rudd's godson punched for standing up for marriage equality in Brisbane",
        'url': 'https://www.pedestrian.tv/news/kevin-rudd-says-godson-bashed-standing-marriage-equality/',
        'source_date': '2017-09-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2017-09-15',
        'location': 'Bulimba, Brisbane, Queensland',
        'victim_identity': 'general_lgbtiq',
        'description': "During Australia's marriage equality postal survey, 19-year-old Sean, godson of former PM Kevin Rudd, was punched at a bus stop in Bulimba after confronting a 48-year-old man who was pulling down rainbow flags from a roundabout and yelling homophobic slurs. Sean suffered a significant gash on his head. The attacker was charged with assault and public nuisance. Rudd called it evidence of what the postal vote could unleash.",
        'severity': 'medium',
        'perpetrator_info': '48-year-old man, charged',
        'latitude': '-27.4540',
        'longitude': '153.0590',
    },
    {
        'title': 'Borna Kazerani assaulted in homophobic attack at Parklea Markets Sydney',
        'url': 'https://www.starobserver.com.au/news/man-assaulted-in-alleged-homophobic-attack-at-parklea-markets/225688',
        'source_date': '2023-08-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-08-06',
        'location': 'Parklea, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': "Borna Kazerani was attacked by Cortez Solomon and Paris Te Atahu Makene Stone in a carpark after visiting Parklea Markets. Solomon punched, kicked, and used homophobic slurs including 'homo' and 'poofter.' Stone pulled Kazerani's hair. Despite calling 000, police never came due to staffing. Solomon was sentenced to 18 months CCO and Stone to 15 months CCO. Magistrate called it 'pretty cowardly.'",
        'severity': 'medium',
        'perpetrator_info': 'Cortez Solomon and Paris Te Atahu Makene Stone, sentenced',
        'latitude': '-33.7295',
        'longitude': '150.9294',
    },
    {
        'title': 'Reality TV star David Subritzky gay bashed on Oxford Street Sydney',
        'url': 'https://www.starobserver.com.au/news/national-news/reality-tv-star-david-subritzky-gay-bashed-in-sydney/223264',
        'source_date': '2023-04-18T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-04-17',
        'location': 'Oxford Street, Darlinghurst, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': "Former I'm A Celebrity contestant David Subritzky, 28, was punched in the face by an unidentified man who hurled homophobic slurs at Five Star Kebabs on Oxford Street around 3am. The attacker fled before police arrived. The incident was part of a wave of anti-LGBTQ attacks in Sydney's gaybourhood, prompting NSW Police to deploy more personnel on Oxford Street.",
        'severity': 'medium',
        'perpetrator_info': 'Unknown man, fled scene',
        'latitude': '-33.8795',
        'longitude': '151.2177',
    },
    {
        'title': 'Plumber fined for homophobic attack on gay man over rainbow house on Phillip Island',
        'url': 'https://www.starobserver.com.au/news/plumber-fined-for-homophobic-attack-on-gay-man-over-rainbow-home/204199',
        'source_date': '2021-07-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2021-07-01',
        'location': 'Phillip Island, Victoria',
        'victim_identity': 'gay',
        'description': "Plumber Jai Ryan, 24, pleaded guilty to unlawful assault after a homophobic attack on Melbourne hairdresser Mykey O'Halloran at his Phillip Island home. Ryan had verbally attacked O'Halloran over plans to paint his house in rainbow colours. Ryan told police he didn't like gay people because they 'freak him out.' Magistrate called his actions 'uneducated, ignorant and breathlessly stupid.' Ryan was fined $2,500. O'Halloran was later also subject to a machete attack in November.",
        'severity': 'medium',
        'perpetrator_info': 'Jai Ryan, 24, plumber, convicted',
        'latitude': '-38.4899',
        'longitude': '145.2331',
    },
    {
        'title': 'Queensland gay couple sent abusive homophobic letters after marriage equality postal survey result',
        'url': 'https://www.sbs.com.au/voices/article/qld-gay-couple-receive-abusive-homophobic-letters-after-postal-survey-result/6e3lm7xcl',
        'source_date': '2017-12-01T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2017-12-01',
        'location': 'Maroochydore, Queensland',
        'victim_identity': 'gay',
        'description': "A gay couple in Maroochydore who said they 'fly very much below the radar' received four homophobic letters after the majority Yes result in the marriage equality postal survey. The letters contained horrific homophobic rhetoric and abuse, demonstrating that hate intensified even after the positive vote.",
        'severity': 'low',
        'perpetrator_info': 'Unknown letter writers',
        'latitude': '-26.6590',
        'longitude': '153.0914',
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
