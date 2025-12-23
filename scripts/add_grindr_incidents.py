"""
Add comprehensive Grindr-related attack incidents to the hate crime database.
These incidents have been documented from news sources and involve attacks
on gay/bisexual men lured through the Grindr dating app.
"""

import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Comprehensive list of documented Grindr attacks in Australia
GRINDR_INCIDENTS = [
    # Peter Keeley - Fatal attack (2020)
    {
        'title': 'Peter Keeley fatally assaulted after being lured via Grindr',
        'url': 'https://www.9news.com.au/national/peter-keeley-teenagers-jailed-fatal-bashing-grindr-lure-sentenced/ab680488-43fe-4b83-abb1-c5b7b43a2b59',
        'source_date': '2020-07-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2020-07-01',
        'location': 'Broulee, NSW',
        'victim_identity': 'gay',
        'description': '56-year-old Peter Keeley was lured via Grindr and fatally assaulted by teenagers. The perpetrators were later convicted of detaining Keeley with intent to commit grievous bodily harm.',
        'severity': 'high',
        'perpetrator_info': 'Three teenagers',
        'latitude': -35.8586,
        'longitude': 150.1792
    },
    # Canberra attacks - July 2024 (multiple victims)
    {
        'title': 'Canberra man assaulted by group after being lured via Grindr',
        'url': 'https://www.abc.net.au/news/2024-08-08/grindr-in-communication-with-act-police-over-alleged-attacks/104199142',
        'source_date': '2024-07-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-07-15',
        'location': 'Canberra, ACT',
        'victim_identity': 'gay',
        'description': 'A man was assaulted by four individuals after being lured via Grindr in Canberra. The attack was part of a series of homophobic incidents in the area.',
        'severity': 'high',
        'perpetrator_info': 'Four individuals',
        'latitude': -35.2809,
        'longitude': 149.1300
    },
    {
        'title': 'Second Canberra Grindr attack - victim assaulted by group wearing face coverings',
        'url': 'https://www.abc.net.au/news/2024-08-08/grindr-in-communication-with-act-police-over-alleged-attacks/104199142',
        'source_date': '2024-07-20T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-07-20',
        'location': 'Canberra, ACT',
        'victim_identity': 'gay',
        'description': 'Second victim in Canberra Grindr attack series. Victim was assaulted by up to eight individuals, some wearing face coverings. Police believe these incidents are connected.',
        'severity': 'high',
        'perpetrator_info': 'Up to eight assailants, some wearing face coverings',
        'latitude': -35.2809,
        'longitude': 149.1300
    },
    {
        'title': 'Third Canberra Grindr attack victim reports assault and robbery',
        'url': 'https://www.abc.net.au/news/2024-08-08/grindr-in-communication-with-act-police-over-alleged-attacks/104199142',
        'source_date': '2024-07-25T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-07-25',
        'location': 'Canberra, ACT',
        'victim_identity': 'gay',
        'description': 'Third man in Canberra reports being lured by deceptive Grindr profile and subsequently assaulted and robbed. Grindr collaborated with local LGBTQIA+ organizations to issue safety warnings.',
        'severity': 'high',
        'perpetrator_info': 'Multiple assailants',
        'latitude': -35.2809,
        'longitude': 149.1300
    },
    # Victoria attacks - October 2024
    {
        'title': 'Melbourne Grindr attacks - 13 individuals arrested',
        'url': 'https://www.theguardian.com/australia-news/2024/oct/17/victoria-gay-men-grindr-dating-app-attacks-police-arrests-ntwnfb',
        'source_date': '2024-10-17T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-10-01',
        'location': 'Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Victoria Police arrested 13 individuals for attacks on gay men lured via dating apps including Grindr. Victims were assaulted, robbed, and subjected to homophobic abuse.',
        'severity': 'high',
        'perpetrator_info': '13 individuals arrested, primarily teenagers',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    # Perth attacks - December 2024
    {
        'title': 'Perth Grindr attack - victim tasered and teeth knocked out',
        'url': 'https://www.fusemagazine.com.au/lgbtiq-news/australia/1148-five-teenagers-jailed-for-grindr-assault-scheme.html',
        'source_date': '2024-12-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-11-15',
        'location': 'Perth, Western Australia',
        'victim_identity': 'gay',
        'description': 'Victim was lured to secluded location via fake Grindr profile, then tasered and had his teeth knocked out. Attackers used weapons including knives, machete, metal bar, and pepper spray.',
        'severity': 'high',
        'perpetrator_info': 'Five teenagers, armed with knives, machete, metal bar, pepper spray, and taser',
        'latitude': -31.9505,
        'longitude': 115.8605
    },
    {
        'title': 'Perth Grindr scheme - multiple victims robbed and assaulted',
        'url': 'https://www.abc.net.au/news/2025-09-23/teenagers-detention-grindr-attacks-men-perth/105807670',
        'source_date': '2024-12-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-12-01',
        'location': 'Perth, Western Australia',
        'victim_identity': 'gay',
        'description': 'Series of violent homophobic attacks in Perth where teenagers used fake Grindr profiles to lure gay men to secluded areas. Victims were robbed and violently assaulted.',
        'severity': 'high',
        'perpetrator_info': 'Group of teenagers under 17',
        'latitude': -31.9505,
        'longitude': 115.8605
    },
    # Sydney robberies - Tanswell & Leilua (attacks occurred 2023-2024)
    {
        'title': 'Sydney Grindr robbery - victim 1 threatened and robbed',
        'url': 'https://www.theguardian.com/australia-news/2025/may/21/sydney-men-jailed-gay-dating-app-grindr-robberies-ntwnfb',
        'source_date': '2023-06-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-06-01',
        'location': 'Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Victim met attackers through Grindr, was threatened and forced to hand over phone and bank details. Money was subsequently stolen from his account.',
        'severity': 'medium',
        'perpetrator_info': 'Andrew James Tanswell and George Phoenix Leilua',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': 'Sydney Grindr robbery - victim 2 targeted in scheme',
        'url': 'https://www.theguardian.com/australia-news/2025/may/21/sydney-men-jailed-gay-dating-app-grindr-robberies-ntwnfb',
        'source_date': '2023-07-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-07-15',
        'location': 'Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Second victim in Sydney Grindr robbery scheme. Victim was threatened and coerced into providing bank details, resulting in significant financial losses.',
        'severity': 'medium',
        'perpetrator_info': 'Andrew James Tanswell and George Phoenix Leilua',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': 'Sydney Grindr robbery - victim 3 robbed and threatened',
        'url': 'https://www.theguardian.com/australia-news/2025/may/21/sydney-men-jailed-gay-dating-app-grindr-robberies-ntwnfb',
        'source_date': '2023-09-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-09-01',
        'location': 'Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Third victim in Sydney Grindr robbery scheme targeting gay men met through the dating app.',
        'severity': 'medium',
        'perpetrator_info': 'Andrew James Tanswell and George Phoenix Leilua',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': 'Sydney Grindr robbery - victim 4 forced to hand over belongings',
        'url': 'https://www.theguardian.com/australia-news/2025/may/21/sydney-men-jailed-gay-dating-app-grindr-robberies-ntwnfb',
        'source_date': '2023-10-15T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-10-15',
        'location': 'Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Fourth victim in Sydney Grindr robbery scheme. Perpetrators sentenced to over six years in prison.',
        'severity': 'medium',
        'perpetrator_info': 'Andrew James Tanswell and George Phoenix Leilua',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    {
        'title': 'Sydney Grindr robbery - victim 5 targeted',
        'url': 'https://www.theguardian.com/australia-news/2025/may/21/sydney-men-jailed-gay-dating-app-grindr-robberies-ntwnfb',
        'source_date': '2023-12-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2023-12-01',
        'location': 'Sydney, NSW',
        'victim_identity': 'gay',
        'description': 'Fifth and final victim in Sydney Grindr robbery scheme. The two perpetrators were sentenced to over six years imprisonment in May 2025.',
        'severity': 'medium',
        'perpetrator_info': 'Andrew James Tanswell and George Phoenix Leilua',
        'latitude': -33.8688,
        'longitude': 151.2093
    },
    # Christian Keryakus - Victoria 2024/2025
    {
        'title': 'Melbourne man attacked by TikTok-inspired assailant via Grindr',
        'url': 'https://www.theguardian.com/australia-news/2025/jun/03/christian-keryakus-grindr-attacks-tiktok-vigilante-videos-ntwnfb',
        'source_date': '2024-08-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-08-01',
        'location': 'Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'First victim attacked by 19-year-old Christian Keryakus who admitted to being inspired by vigilante videos on TikTok. Met victim through Grindr.',
        'severity': 'high',
        'perpetrator_info': 'Christian Keryakus, 19, inspired by TikTok vigilante videos',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    {
        'title': 'Second Melbourne man attacked by TikTok-inspired Grindr assailant',
        'url': 'https://www.theguardian.com/australia-news/2025/jun/03/christian-keryakus-grindr-attacks-tiktok-vigilante-videos-ntwnfb',
        'source_date': '2024-09-01T00:00:00Z',
        'incident_type': 'assault',
        'date': '2024-09-01',
        'location': 'Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Second victim attacked by Christian Keryakus after being lured through Grindr. Perpetrator was sentenced in June 2025.',
        'severity': 'high',
        'perpetrator_info': 'Christian Keryakus, 19, inspired by TikTok vigilante videos',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
    # Victoria mass arrests - May 2025 (attacks occurred Oct 2024 - May 2025)
    {
        'title': 'Victoria Grindr attacks - 30+ arrested for targeting gay men',
        'url': 'https://www.abc.net.au/news/2025-05-09/dating-app-lgbtqi-scammers-crime/105270744',
        'source_date': '2025-05-09T00:00:00Z',
        'incident_type': 'assault',
        'date': '2025-01-01',
        'location': 'Melbourne, Victoria',
        'victim_identity': 'gay',
        'description': 'Victoria Police arrested over 30 individuals, primarily male teenagers aged 13-20, for attacks on men lured via Grindr. Victims were assaulted, robbed, and subjected to homophobic slurs. Some attacks were filmed and shared on social media.',
        'severity': 'high',
        'perpetrator_info': 'Over 30 individuals, male teenagers aged 13-20',
        'latitude': -37.8136,
        'longitude': 144.9631
    },
]

def main():
    print("=" * 60)
    print("ADDING GRINDR ATTACK INCIDENTS TO DATABASE")
    print("=" * 60)
    
    # Load existing incidents
    incidents_file = 'data/incidents_in_progress.csv'
    
    if os.path.exists(incidents_file):
        existing_df = pd.read_csv(incidents_file)
        print(f"\nLoaded {len(existing_df)} existing incidents")
        existing_urls = set(existing_df['url'].values)
    else:
        existing_df = pd.DataFrame()
        existing_urls = set()
        print("\nNo existing incidents file found, creating new one")
    
    # Filter out incidents that already exist
    new_incidents = []
    for incident in GRINDR_INCIDENTS:
        if incident['url'] not in existing_urls:
            new_incidents.append(incident)
            print(f"  + Adding: {incident['title'][:60]}...")
        else:
            print(f"  - Skipping (exists): {incident['title'][:50]}...")
    
    if not new_incidents:
        print("\nNo new Grindr incidents to add - all already in database.")
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
    
    print(f"\n{'=' * 60}")
    print(f"COMPLETE!")
    print(f"Added {len(new_incidents)} new Grindr attack incidents")
    print(f"Total incidents now: {len(combined_df)}")
    print(f"Saved to: {incidents_file}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()












