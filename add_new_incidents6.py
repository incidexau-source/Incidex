import csv

new_incidents = [
    {
        'title': 'David Saint bashed to death in Adelaide south parklands in suspected gay hate crime',
        'url': 'https://www.starobserver.com.au/news/national-news/south-australia/sa-police-appeal-for-information-over-unsolved-gay-bashing-murders-of-two-adelaide-men/180265',
        'source_date': '2019-04-16T00:00:00Z',
        'incident_type': 'murder',
        'date': '1991-04-16',
        'location': 'South Parklands, Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': 'David Saint, 41, was bashed to death in Adelaide\'s south parklands on the night of April 16, 1991. Three men were seen assaulting and chasing him across South Terrace before continuing their attack. Two people who tried to intervene were told to mind their own business. Police initially said robbery was the motive, but Saint still had his wallet with $300 cash. The area was a known gay beat and the gay community believed the attack was motivated by homophobia. The murder remains unsolved. A reward of up to $200,000 is on offer via Operation Persist.',
        'severity': 'high',
        'perpetrator_info': 'Three unknown men, unsolved',
        'latitude': '-34.9380',
        'longitude': '138.6000',
    },
    {
        'title': 'Shaine Moore strangled to death by ex-boyfriend in Adelaide',
        'url': 'https://www.thepinknews.com/2011/03/28/australian-gay-man-pleads-guilty-to-erotic-asphyxia-murder/',
        'source_date': '2011-03-28T00:00:00Z',
        'incident_type': 'murder',
        'date': '2005-02-01',
        'location': 'Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': 'Shaine Moore was found dead in his bedroom, strangled with a shoelace. His ex-boyfriend David Richard Fraser confessed in 2007 to killing him, taking a plea deal for manslaughter claiming an auto-erotic sex game gone wrong. Fraser was released on parole after a few years. In 2009, Fraser killed another boyfriend, Luke Noonan, 29, in similar circumstances and was convicted of murder with a minimum 22 years.',
        'severity': 'high',
        'perpetrator_info': 'David Richard Fraser, convicted of manslaughter',
        'latitude': '-34.9285',
        'longitude': '138.6007',
    },
    {
        'title': 'Wayne Ruks bashed to death in churchyard in Maryborough Queensland',
        'url': 'https://www.sbs.com.au/voices/creative/the-end-of-gay-panic/ustkd0nsz',
        'source_date': '2017-03-21T00:00:00Z',
        'incident_type': 'murder',
        'date': '2008-07-03',
        'location': 'Maryborough, Queensland',
        'victim_identity': 'gay',
        'description': 'Wayne Ruks, 45, a disability pensioner, was bashed and left for dead in the grounds of St Mary\'s Catholic Church in Maryborough on the night of July 3, 2008. His body was found by worshippers the next morning. Attackers Richard Meerdink and Jason Pearce claimed Ruks made a homosexual advance, but security camera footage showed no evidence of this. Murder charges were reduced to manslaughter using the controversial "gay panic" defence. Pearce was sentenced to 9 years but released after 4. The case prompted Father Paul Kelly\'s petition with 290,000 signatures, leading Queensland to abolish the gay panic defence in 2017.',
        'severity': 'high',
        'perpetrator_info': 'Richard Meerdink and Jason Pearce, convicted of manslaughter',
        'latitude': '-25.5413',
        'longitude': '152.7021',
    },
    {
        'title': 'Gay couple Craig Gillard and Jamie Ronnfeldt bashed by teenagers in Maryborough Queensland',
        'url': 'https://www.starobserver.com.au/news/gay-bashers-jailed/40411',
        'source_date': '2010-12-16T00:00:00Z',
        'incident_type': 'assault',
        'date': '2008-01-17',
        'location': 'Maryborough, Queensland',
        'victim_identity': 'gay',
        'description': 'Melbourne couple Craig Gillard and Jamie Ronnfeldt were attacked in the early hours of January 17 in Maryborough. One of the youths asked if they had come from a local gay night and called them "faggots" before knocking food out of Gillard\'s hands. He was tripped and kicked several times. Passer-by Ryan Wolstencroft was attacked when he intervened. Ronnfeldt was knocked down when he tried to call police. Isaac Sanderson and Jason Bishop pled guilty; Dylan Hodge was found guilty of assault causing bodily harm and grievous bodily harm.',
        'severity': 'medium',
        'perpetrator_info': 'Four teenagers aged 17-18, three convicted',
        'latitude': '-25.5413',
        'longitude': '152.7021',
    },
    {
        'title': 'Anthony Cawsey fatally stabbed in suspected gay hate crime in Centennial Park Sydney',
        'url': 'https://www.starobserver.com.au/news/national-news/new-south-wales-news/sexuality-a-factor-in-anthony-cawseys-2009-stabbing-death-in-sydney-park-gay-hate-inquiry-told/224647',
        'source_date': '2023-06-01T00:00:00Z',
        'incident_type': 'murder',
        'date': '2009-09-01',
        'location': 'Centennial Park, Sydney, New South Wales',
        'victim_identity': 'gay',
        'description': 'Anthony Cawsey, 37, a stage-hand described as vibrant and charismatic, was found fatally stabbed in Centennial Park in September 2009. He had walked from his Redfern flat to the park, a known gay beat, while phoning a chat line. He was found with a single stab wound to his chest with his pants pulled down. The NSW Special Commission inquiry heard that sexuality was a possible factor. A person of interest, Moses Kellie, was charged in 2015 but the case was dismissed. DNA from three unknown men was found but never matched. The murder remains unsolved.',
        'severity': 'high',
        'perpetrator_info': 'Unknown, unsolved',
        'latitude': '-33.8932',
        'longitude': '151.2295',
    },
    {
        'title': 'Andrew Negre murdered in Adelaide after killer used gay panic defence',
        'url': 'https://www.sbs.com.au/voices/creative/out-of-sight-the-untold-story-of-adelaides-gay-hate-murders/vw9etx2cw',
        'source_date': '2019-01-01T00:00:00Z',
        'incident_type': 'murder',
        'date': '2011-04-01',
        'location': 'Hallett Cove, Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': 'Andrew Roger Negre was murdered on 1 April 2011 at the home of Michael Joseph Lindsay in Hallett Cove after they met at the Hallett Cove Tavern. Negre was stabbed multiple times including wounds that completely severed his aorta, and his throat was cut by co-accused Luke Hutchings. Lindsay used the gay panic defence claiming Negre had straddled him in a sexually suggestive manner. Despite appeals including to the High Court, Lindsay was found guilty of murder in 2016. The case was instrumental in the campaign to abolish the gay panic defence in South Australia, which was achieved in 2020.',
        'severity': 'high',
        'perpetrator_info': 'Michael Joseph Lindsay and Luke Hutchings, convicted of murder',
        'latitude': '-35.0736',
        'longitude': '138.5163',
    },
    {
        'title': 'Luke Noonan strangled by repeat killer David Fraser in Adelaide',
        'url': 'https://www.thepinknews.com/2011/03/28/australian-gay-man-pleads-guilty-to-erotic-asphyxia-murder/',
        'source_date': '2011-03-28T00:00:00Z',
        'incident_type': 'murder',
        'date': '2009-09-01',
        'location': 'Adelaide, South Australia',
        'victim_identity': 'gay',
        'description': 'Luke Noonan, 29, was strangled during a sex act involving erotic asphyxia by David Richard Fraser, 36, in September 2009. Fraser had previously killed his boyfriend Shaine Moore in similar circumstances in 2005 and received only a manslaughter conviction. For Noonan\'s killing, Fraser initially denied murder but changed his plea to guilty. He was sentenced to murder with a minimum 22 years imprisonment.',
        'severity': 'high',
        'perpetrator_info': 'David Richard Fraser, convicted of murder, minimum 22 years',
        'latitude': '-34.9285',
        'longitude': '138.6007',
    },
    {
        'title': 'Gay man Joshua and brother bashed by teenagers at Coomera Westfield Gold Coast',
        'url': 'https://qnews.com.au/gay-man-bashed-in-bloodthirsty-homophobic-gold-coast-attack/',
        'source_date': '2021-01-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2021-01-01',
        'location': 'Coomera, Gold Coast, Queensland',
        'victim_identity': 'gay',
        'description': 'A gay man named Joshua said he would not return to Queensland after he and his 16-year-old brother were brutally bashed at Coomera Westfield shopping centre on the Gold Coast. The teenagers had earlier yelled homophobic slurs and attacked them on a bus, then hunted them down at the shopping centre to continue the assault.',
        'severity': 'medium',
        'perpetrator_info': 'Group of teenagers',
        'latitude': '-27.8614',
        'longitude': '153.3453',
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
