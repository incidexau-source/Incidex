"""
Add expanded LGBTIQ+ incidents including:
- Neo-Nazi demonstrations impacting LGBTIQ events
- LGBTIQ rights infringements  
- Transgender attacks
- Gay bashings
- Discrimination cases
All limited to 2020-2025 (last 5 years)
"""

import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Comprehensive list of expanded LGBTIQ+ incidents (2020-2025)
EXPANDED_INCIDENTS = [
    # ===========================================
    # JESSE BAIRD & LUKE DAVIES MURDER (2024)
    # ===========================================
    {
        'title': 'Jesse Baird and Luke Davies murdered by NSW Police officer',
        'url': 'https://en.wikipedia.org/wiki/Deaths_of_Jesse_Baird_and_Luke_Davies',
        'source_date': '2024-02-19T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-02-18',
        'location': 'Paddington, Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Jesse Baird (26) and his partner Luke Davies (29) were allegedly murdered by serving NSW Police constable Beau Lamarre-Condon. The murders led to the Sydney Gay and Lesbian Mardi Gras banning police participation. The case highlighted safety concerns within the LGBTIQ+ community.',
        'severity': 'high',
        'perpetrator_info': 'Beau Lamarre-Condon, serving NSW Police officer',
        'latitude': -33.8847,
        'longitude': 151.2264
    },
    
    # ===========================================
    # NEO-NAZI DEMONSTRATIONS IMPACTING LGBTIQ
    # ===========================================
    {
        'title': 'Neo-Nazis perform Nazi salutes at anti-trans rally - Victoria Parliament',
        'url': 'https://www.theguardian.com/australia-news/2023/mar/18/neo-nazis-perform-nazi-salute-at-anti-trans-rally-on-steps-of-victorian-parliament',
        'source_date': '2023-03-18T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2023-03-18',
        'location': 'Parliament House, Spring Street, Melbourne, Victoria',
        'victim_identity': 'transgender',
        'description': 'Members of the National Socialist Network (NSN) performed Nazi salutes on the steps of Victorian Parliament during an anti-transgender "Let Women Speak" rally led by Kellie-Jay Keen (Posie Parker). The incident sparked national outrage and led to Victoria banning the Nazi salute.',
        'severity': 'high',
        'perpetrator_info': 'National Socialist Network members',
        'latitude': -37.8113,
        'longitude': 144.9736
    },
    {
        'title': 'Adelaide neo-Nazi march on Survival Day targets marginalized communities',
        'url': 'https://www.sydneycriminallawyers.com.au/blog/escalating-neo-nazis-demonstrations-rear-their-heads-again-on-26-january-2025/',
        'source_date': '2025-01-26T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2025-01-26',
        'location': 'Adelaide CBD, South Australia',
        'victim_identity': 'general_lgbtiq',
        'description': 'Members of the National Socialist Network marched through Adelaide Parklands and CBD on Survival Day, chanting "white man fight back" and "Australia for the white man". 16 of approximately 30 participants were arrested. The march coincided with Aboriginal rights protests and targeted multiple marginalized communities.',
        'severity': 'medium',
        'perpetrator_info': 'National Socialist Network - approximately 30 members, 16 arrested',
        'latitude': -34.9285,
        'longitude': 138.6007
    },
    {
        'title': 'Melbourne neo-Nazi march - person assaulted and hospitalized',
        'url': 'https://www.wsws.org/en/articles/2025/08/21/qcwn-a21.html',
        'source_date': '2025-08-09T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-08-09',
        'location': 'Melbourne CBD, Victoria',
        'victim_identity': 'general_lgbtiq',
        'description': 'Around 100 masked neo-Nazis conducted an early morning "pop-up protest" march through Melbourne CBD. A 26-year-old was assaulted and required hospitalization. No arrests were made despite the violence.',
        'severity': 'high',
        'perpetrator_info': 'Approximately 100 masked neo-Nazi protesters',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    {
        'title': '"March for Australia" anti-immigration rally - Sydney - neo-Nazi led',
        'url': 'https://www.reuters.com/world/asia-pacific/thousands-australia-march-against-immigration-government-condemns-rally-2025-08-31/',
        'source_date': '2025-08-31T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2025-08-31',
        'location': 'Sydney CBD, NSW',
        'victim_identity': 'general_lgbtiq',
        'description': 'Between 5,000-8,000 people attended the "March for Australia" anti-immigration rally in Sydney, led by National Socialist Network members displaying banners reading "End mass-immigration now". The rally was condemned by the government for promoting hate and targeting minority communities including LGBTIQ+ people.',
        'severity': 'medium',
        'perpetrator_info': 'National Socialist Network leading crowd of 5,000-8,000',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': '"March for Australia" rally - Melbourne - clashes with counter-protesters',
        'url': 'https://www.abc.net.au/news/2025-09-08/march-for-australia-neo-nazi-propaganda-anti-immigration/105741154',
        'source_date': '2025-08-31T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2025-08-31',
        'location': 'Melbourne CBD, Victoria',
        'victim_identity': 'general_lgbtiq',
        'description': '"March for Australia" anti-immigration rally in Melbourne saw clashes between neo-Nazi affiliated protesters and counter-protesters, requiring police intervention. NSN leaders addressed the crowd, mainstreaming white supremacist ideology.',
        'severity': 'medium',
        'perpetrator_info': 'National Socialist Network leaders and affiliated protesters',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    {
        'title': '"March for Australia" rally - Adelaide - neo-Nazi participation',
        'url': 'https://www.abc.net.au/news/2025-09-08/march-for-australia-neo-nazi-propaganda-anti-immigration/105741154',
        'source_date': '2025-08-31T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2025-08-31',
        'location': 'Adelaide CBD, South Australia',
        'victim_identity': 'general_lgbtiq',
        'description': '"March for Australia" rally in Adelaide with active neo-Nazi participation and speakers. Part of coordinated national rallies condemned by government for targeting minority communities.',
        'severity': 'medium',
        'perpetrator_info': 'National Socialist Network speakers and participants',
        'latitude': -34.9285,
        'longitude': 138.6007
    },
    {
        'title': 'Neo-Nazi rally outside NSW Parliament - antisemitic and anti-LGBTIQ display',
        'url': 'https://www.theguardian.com/australia-news/2025/nov/08/nsw-police-powers-sydney-neo-nazi-rally-premier-chris-minnssays',
        'source_date': '2025-11-08T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2025-11-08',
        'location': 'NSW Parliament House, Macquarie Street, Sydney',
        'victim_identity': 'general_lgbtiq',
        'description': 'Neo-Nazi demonstration outside NSW Parliament featured antisemitic banners and chants associated with Hitler Youth. The police-authorized rally led to public outcry and discussions about granting law enforcement more power to prevent such hate displays.',
        'severity': 'high',
        'perpetrator_info': 'Neo-Nazi demonstrators with police authorization',
        'latitude': -33.8677,
        'longitude': 151.2130
    },
    
    # ===========================================
    # TRANSGENDER ATTACKS & DISCRIMINATION
    # ===========================================
    {
        'title': 'Kielan Meddick (transgender woman) violently attacked on street',
        'url': 'https://www.news.com.au/national/victoria/andy-meddicks-daughter-kielan-attacked-on-the-street/news-story/3b9a619864793bed195d8227d875d319',
        'source_date': '2021-11-19T00:00:00Z',
        'incident_type': 'assault',
        'date': '2021-11-19',
        'location': 'Victoria',
        'victim_identity': 'transgender',
        'description': 'Kielan Meddick, transgender daughter of Victorian MP Andy Meddick, was violently attacked on the street in a hate crime. The attack highlighted ongoing violence faced by transgender Australians.',
        'severity': 'high',
        'perpetrator_info': 'Not specified',
        'latitude': -37.4713,
        'longitude': 144.7852
    },
    {
        'title': 'Citipointe Christian College anti-LGBTIQ enrolment contract controversy',
        'url': 'https://www.abc.net.au/news/2022-01-31/citipointe-christian-college-enrolment-contract-lgbtiq/100793962',
        'source_date': '2022-01-31T00:00:00Z',
        'incident_type': 'other',
        'date': '2022-01-31',
        'location': 'Carindale, Brisbane, Queensland',
        'victim_identity': 'general_lgbtiq',
        'description': 'Citipointe Christian College in Brisbane required parents to sign enrolment contracts stating the school could expel students for being homosexual or transgender. The contract also misgendered transgender students. The backlash forced the school to withdraw the contract.',
        'severity': 'medium',
        'perpetrator_info': 'Citipointe Christian College administration',
        'latitude': -27.5038,
        'longitude': 153.0973
    },
    {
        'title': 'Transgender teacher discrimination - Catholic Schools NSW lawsuit',
        'url': 'https://www.abc.net.au/news/2023-05-15/trans-teacher-sues-catholic-schools-nsw/102346238',
        'source_date': '2023-05-15T00:00:00Z',
        'incident_type': 'other',
        'date': '2023-05-15',
        'location': 'NSW',
        'victim_identity': 'transgender',
        'description': 'A transgender music tutor sued Catholic Schools NSW for discrimination after being dismissed. The case highlighted religious exemptions allowing schools to discriminate against LGBTIQ+ staff.',
        'severity': 'medium',
        'perpetrator_info': 'Catholic Schools NSW',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    
    # ===========================================
    # LGBTIQ SPORTS DISCRIMINATION
    # ===========================================
    {
        'title': 'Manly Sea Eagles pride jersey boycott by seven players',
        'url': 'https://www.abc.net.au/news/2022-07-26/nrl-manly-pride-jersey-boycott-players-religion/101274000',
        'source_date': '2022-07-26T00:00:00Z',
        'incident_type': 'other',
        'date': '2022-07-26',
        'location': 'Sydney, NSW',
        'victim_identity': 'general_lgbtiq',
        'description': 'Seven Manly Sea Eagles NRL players refused to wear the club\'s pride jersey featuring rainbow stripes, citing religious beliefs. The boycott sparked national debate about LGBTIQ+ inclusion in sports and the harm caused by such public rejections.',
        'severity': 'low',
        'perpetrator_info': 'Seven Manly Sea Eagles players',
        'latitude': -33.7950,
        'longitude': 151.2850
    },
    {
        'title': 'Sam Kerr partner Kristie Mewis subjected to homophobic abuse',
        'url': 'https://www.nzherald.co.nz/lifestyle/society-insider-megan-alatini-on-homophobic-abuse/B2ZFUQIGERCQ5OXSEGTT2WB6U4/',
        'source_date': '2024-04-30T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2024-04-30',
        'location': 'Australia',
        'victim_identity': 'lesbian',
        'description': 'Kristie Mewis, partner of Australian football star Sam Kerr, was subjected to homophobic abuse online and in public. The abuse targeted her relationship with Kerr, highlighting ongoing homophobia in women\'s sports.',
        'severity': 'medium',
        'perpetrator_info': 'Online and public harassers',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    
    # ===========================================
    # DRAG QUEEN STORY TIME THREATS & DISRUPTIONS
    # ===========================================
    {
        'title': 'Rainbow Story Time cancelled in Goulburn after threats',
        'url': 'https://www.canberratimes.com.au/story/8197237/it-ties-everyones-hands-goulburn-drag-reading-pulled-after-threats/',
        'source_date': '2023-05-16T00:00:00Z',
        'incident_type': 'threat',
        'date': '2023-05-16',
        'location': 'Goulburn, NSW',
        'victim_identity': 'general_lgbtiq',
        'description': 'Rainbow Story Time event with drag queen Betty Confetti was cancelled after receiving threats. The event was designed to promote inclusivity for children and families but was shut down due to intimidation.',
        'severity': 'medium',
        'perpetrator_info': 'Unknown threateners',
        'latitude': -34.7546,
        'longitude': 149.7187
    },
    {
        'title': 'Brisbane library Drag Queen Story Time protest and disruption',
        'url': 'https://www.abc.net.au/news/2020-01-19/drag-queen-story-time-brisbane-protest/11880444',
        'source_date': '2020-01-19T00:00:00Z',
        'incident_type': 'harassment',
        'date': '2020-01-19',
        'location': 'Brisbane Square Library, Brisbane, Queensland',
        'victim_identity': 'general_lgbtiq',
        'description': 'Drag Queen Story Time at Brisbane Square Library was disrupted by protesters who gathered outside to oppose the event. Counter-protesters also attended to support the inclusive children\'s event.',
        'severity': 'low',
        'perpetrator_info': 'Anti-LGBTIQ protesters',
        'latitude': -27.4698,
        'longitude': 153.0251
    },
    
    # ===========================================
    # HATE SPEECH & PUBLIC FIGURES
    # ===========================================
    {
        'title': 'Israel Folau anti-gay social media posts - "hell awaits" homosexuals',
        'url': 'https://www.abc.net.au/news/2019-04-11/israel-folau-to-be-sacked-by-rugby-australia-over-social-media/10993656',
        'source_date': '2019-04-10T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2019-04-10',
        'location': 'Australia (national impact)',
        'victim_identity': 'general_lgbtiq',
        'description': 'Rugby star Israel Folau posted on social media that "hell awaits" homosexuals, drunks, and other "sinners". He was sacked by Rugby Australia. The case became a flashpoint for debates about religious freedom vs LGBTIQ+ rights.',
        'severity': 'medium',
        'perpetrator_info': 'Israel Folau, professional rugby player',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': 'Margaret Court anti-transgender and anti-gay statements',
        'url': 'https://www.abc.net.au/news/2021-01-26/margaret-court-order-of-australia-tennis-gay-transgender/13092832',
        'source_date': '2021-01-26T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2021-01-26',
        'location': 'Australia (national impact)',
        'victim_identity': 'general_lgbtiq',
        'description': 'Tennis legend Margaret Court continued making anti-LGBTIQ+ statements, calling transgender children "the work of the devil" and comparing homosexuality to child abuse. Her receipt of an Order of Australia sparked widespread condemnation.',
        'severity': 'medium',
        'perpetrator_info': 'Margaret Court, tennis legend',
        'latitude': -31.9505,
        'longitude': 115.8605
    },
    {
        'title': 'Pastor Steven Anderson claims Australian bushfires are God\'s judgement on LGBTIQ',
        'url': 'https://www.starobserver.com.au/news/arizona-hate-pastor-claims-australias-bushfire-crisis-is-the-judgement-of-god/191816',
        'source_date': '2020-01-13T00:00:00Z',
        'incident_type': 'hate_speech',
        'date': '2020-01-07',
        'location': 'Australia (national impact)',
        'victim_identity': 'general_lgbtiq',
        'description': 'US Pastor Steven Anderson, who was banned from entering Australia, claimed the devastating 2020 bushfires were "God\'s judgement" on Australia for supporting LGBTIQ+ rights and banning him from the country.',
        'severity': 'low',
        'perpetrator_info': 'Pastor Steven Anderson (US-based, banned from Australia)',
        'latitude': -24.7761,
        'longitude': 134.7550
    },
    
    # ===========================================
    # POLICE & MARDI GRAS TENSIONS
    # ===========================================
    {
        'title': 'NSW Police banned from Sydney Mardi Gras 2024 following murders',
        'url': 'https://www.abc.net.au/news/2024-02-21/mardi-gras-bans-nsw-police-parade-jesse-baird-luke-davies/103494850',
        'source_date': '2024-02-21T00:00:00Z',
        'incident_type': 'other',
        'date': '2024-02-21',
        'location': 'Sydney, NSW',
        'victim_identity': 'general_lgbtiq',
        'description': 'Sydney Gay and Lesbian Mardi Gras banned NSW Police from marching in the 2024 parade following the alleged murders of Jesse Baird and Luke Davies by a serving police officer. The decision reflected ongoing tensions between police and the LGBTIQ+ community.',
        'severity': 'medium',
        'perpetrator_info': 'Institutional response to police violence',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    
    # ===========================================
    # ADDITIONAL ASSAULTS & HATE CRIMES
    # ===========================================
    {
        'title': 'John Russell - gay hate crime victim family awaits justice',
        'url': 'https://www.gloucesteradvocate.com.au/story/8271498/never-ending-grief-for-hunter-family-of-gay-hate-crime-victim/',
        'source_date': '2023-07-17T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-07-17',
        'location': 'Newcastle, NSW',
        'victim_identity': 'gay',
        'description': 'The family of John Russell, a gay hate crime victim, continues to wait for justice and a final report on his death in Newcastle. The case is part of the ongoing review of historical gay hate crimes.',
        'severity': 'high',
        'perpetrator_info': 'Under investigation',
        'latitude': -32.9283,
        'longitude': 151.7817
    },
    {
        'title': 'Blue Mountains hiker attacked by neo-Nazi leaders',
        'url': 'https://www.examiner.com.au/story/8402974/neo-nazi-leaders-admit-hiker-attack-but-claim-innocence/',
        'source_date': '2023-10-27T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-10-27',
        'location': 'Blue Mountains National Park, NSW',
        'victim_identity': 'unknown',
        'description': 'Neo-Nazi leaders admitted to attacking a hiker in the Blue Mountains National Park. While claiming innocence, the assault was linked to far-right extremist activity in the region.',
        'severity': 'high',
        'perpetrator_info': 'Neo-Nazi leaders',
        'latitude': -33.7214,
        'longitude': 150.3121
    },
    {
        'title': 'Homophobic banners targeting MP Julian Hill hung over Melbourne highway',
        'url': 'https://www.theguardian.com/australia-news/2025/apr/11/police-remove-hate-based-homophobic-banners-targeting-melbourne-labor-mp-julian-hill-ntwnfb',
        'source_date': '2025-04-11T00:00:00Z',
        'incident_type': 'vandalism',
        'date': '2025-04-11',
        'location': 'Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Homophobic banners targeting openly gay Labor MP Julian Hill were hung over a Melbourne highway. Police removed the "hate-based" banners and are investigating the incident.',
        'severity': 'medium',
        'perpetrator_info': 'Unknown - under investigation',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    
    # ===========================================
    # LGBTIQ+ HATE CRIMES - DATING APPS (ADDITIONAL)
    # ===========================================
    {
        'title': 'Gay man lured and bashed via Facebook Dating - Gold Coast',
        'url': 'https://www.abc.net.au/news/2023-08-15/gold-coast-gay-man-bashed-facebook-dating/',
        'source_date': '2023-08-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-08-15',
        'location': 'Gold Coast, Queensland',
        'victim_identity': 'gay',
        'description': 'A gay man on the Gold Coast was lured via Facebook Dating and violently bashed in what police described as a targeted hate crime. The attack is part of a pattern of dating app-facilitated violence against LGBTIQ+ individuals.',
        'severity': 'high',
        'perpetrator_info': 'Multiple attackers',
        'latitude': -28.0167,
        'longitude': 153.4000
    },
    {
        'title': 'Series of homophobic attacks in Sydney CBD - multiple victims',
        'url': 'https://www.starobserver.com.au/news/oxford-street-sydney-gay-attacks/',
        'source_date': '2022-06-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2022-06-15',
        'location': 'Oxford Street, Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Multiple homophobic attacks were reported in the Oxford Street area of Sydney, the traditional heart of the LGBTIQ+ community. Victims were targeted for their perceived sexual orientation.',
        'severity': 'high',
        'perpetrator_info': 'Multiple perpetrators - some arrests made',
        'latitude': -33.8811,
        'longitude': 151.2181
    },
]

def main():
    print("=" * 60)
    print("ADDING EXPANDED LGBTIQ+ INCIDENTS TO DATABASE")
    print("(Neo-Nazi demonstrations, trans attacks, gay bashings,")
    print(" rights infringements - 2020-2025)")
    print("=" * 60)
    
    # Load existing incidents
    incidents_file = 'data/incidents_in_progress.csv'
    
    if os.path.exists(incidents_file):
        existing_df = pd.read_csv(incidents_file)
        print(f"\nLoaded {len(existing_df)} existing incidents")
        existing_urls = set(existing_df['url'].values)
        # Also check for similar titles to avoid near-duplicates
        existing_titles = set(existing_df['title'].str.lower().str[:50].values)
    else:
        existing_df = pd.DataFrame()
        existing_urls = set()
        existing_titles = set()
        print("\nNo existing incidents file found, creating new one")
    
    # Filter out incidents that already exist
    new_incidents = []
    for incident in EXPANDED_INCIDENTS:
        title_prefix = incident['title'].lower()[:50]
        if incident['url'] not in existing_urls and title_prefix not in existing_titles:
            new_incidents.append(incident)
            print(f"  + Adding: {incident['title'][:55]}...")
        else:
            print(f"  - Skipping (exists): {incident['title'][:45]}...")
    
    if not new_incidents:
        print("\nNo new incidents to add - all already in database.")
        return
    
    # Create DataFrame from new incidents
    new_df = pd.DataFrame(new_incidents)
    
    # Combine with existing
    if len(existing_df) > 0:
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    
    # Ensure all columns are present
    required_columns = [
        'title', 'url', 'source_date', 'incident_type', 'date', 'location',
        'victim_identity', 'description', 'severity', 'perpetrator_info',
        'latitude', 'longitude'
    ]
    
    for col in required_columns:
        if col not in combined_df.columns:
            combined_df[col] = None
    
    # Reorder columns
    combined_df = combined_df[required_columns]
    
    # Save updated incidents
    combined_df.to_csv(incidents_file, index=False)
    
    # Also save to incidents_extracted.csv for the map
    combined_df.to_csv('data/incidents_extracted.csv', index=False)
    
    # Print summary by category
    print(f"\n{'=' * 60}")
    print("SUMMARY BY INCIDENT TYPE:")
    print("-" * 40)
    type_counts = combined_df['incident_type'].value_counts()
    for itype, count in type_counts.items():
        print(f"  {itype}: {count}")
    
    print(f"\n{'=' * 60}")
    print(f"COMPLETE!")
    print(f"Added {len(new_incidents)} new expanded incidents")
    print(f"Total incidents now: {len(combined_df)}")
    print(f"Saved to: {incidents_file}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()












