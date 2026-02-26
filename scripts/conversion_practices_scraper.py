"""
Conversion Practices Incident Scraper

Extracts documented conversion practices/therapy incidents from Australia.
Sources: News reports, survivor testimonies, advocacy organizations.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict

# Documented conversion practices incidents in Australia
CONVERSION_PRACTICES_INCIDENTS = [
    {
        "title": "Andrew Barnard - C3 Church conversion practices survivor",
        "url": "https://www.starobserver.com.au/news/church-would-like-public-to-believe-conversion-practices-are-therapies-says-survivor/204318",
        "source_date": "2021-07-01",
        "incident_type": "conversion_practices",
        "date": "2005-01-01",  # Approximate - occurred during his time at C3 Church
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Andrew Barnard, a former member of C3 Church in Sydney, was subjected to conversion practices from age 13. He twice attempted suicide after church therapists told him his sexuality was due to 'nurture' and childhood experiences. He suffered severe depression, internalized homophobia, and self-loathing.",
        "severity": "high",
        "perpetrator_info": "C3 Church Sydney - therapy program",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "cross_reference": "Star Observer; ABBI"
    },
    {
        "title": "Anthony Venn-Brown - Assemblies of God conversion practices (1972-1999)",
        "url": "https://www.abbi.org.au/conversion-therapy/",
        "source_date": "2022-03-01",
        "incident_type": "conversion_practices",
        "date": "1972-01-01",
        "location": "Adelaide, SA",
        "victim_identity": "gay_man",
        "description": "Anthony Venn-Brown OAM was subjected to conversion practices for 27 years after attending a church meeting in Adelaide featuring 'ex-gay' speaker Sy Rogers. In 2022, a church officially apologized for the harm caused. Venn-Brown became a leading advocate for banning conversion practices in Australia.",
        "severity": "high",
        "perpetrator_info": "Assemblies of God / Pentecostal churches",
        "latitude": -34.9285,
        "longitude": 138.6007,
        "cross_reference": "ABBI; Church apology 2022"
    },
    {
        "title": "Trans woman subjected to conversion practices - Melbourne",
        "url": "https://www.mamamia.com.au/conversion-therapy-australia/",
        "source_date": "2020-01-01",
        "incident_type": "conversion_practices",
        "date": "2015-01-01",  # Approximate
        "location": "Melbourne, VIC",
        "victim_identity": "trans_woman",
        "description": "A transgender woman was subjected to conversion practices in Melbourne by a religious organization that attempted to change her gender identity. The practices caused lasting psychological trauma and mental health issues.",
        "severity": "high",
        "perpetrator_info": "Religious organization",
        "latitude": -37.8136,
        "longitude": 144.9631,
        "cross_reference": "Mamamia investigation"
    },
    {
        "title": "Victoria conversion practices survivor testimony - Religious setting",
        "url": "https://www.humanrights.vic.gov.au/change-or-suppression-practices/change-or-suppression-stories/",
        "source_date": "2021-01-01",
        "incident_type": "conversion_practices",
        "date": "2018-01-01",
        "location": "Victoria",
        "victim_identity": "general_lgbtiq",
        "description": "Survivor testimony documented by Victorian Equal Opportunity and Human Rights Commission of change or suppression practices in religious settings. Victim experienced pressure to change their sexual orientation through prayer, counselling and pastoral interventions.",
        "severity": "high",
        "perpetrator_info": "Religious institution (details protected)",
        "latitude": -37.4713,
        "longitude": 144.7852,
        "cross_reference": "VEOHRC Change or Suppression Practices documentation"
    },
    {
        "title": "NSW conversion practices - 40 survivors lodge submissions",
        "url": "https://equalityaustralia.org.au/survivors-and-equality-australia-welcome-conversion-ban-taking-effect-in-nsw/",
        "source_date": "2024-03-22",
        "incident_type": "conversion_practices",
        "date": "2020-01-01",  # Representative date for ongoing practices
        "location": "New South Wales",
        "victim_identity": "general_lgbtiq",
        "description": "Around 40 survivors of conversion practices in NSW lodged submissions and attended roundtables during the campaign to ban conversion therapy. Their testimonies documented practices in religious, pastoral, and informal settings causing long-term psychological harm, trauma, shame, and isolation.",
        "severity": "high",
        "perpetrator_info": "Various religious and pastoral organizations in NSW",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "cross_reference": "Equality Australia; NSW Conversion Practices Ban Bill 2024"
    },
    {
        "title": "Hillsong Church conversion practices allegations - Sydney",
        "url": "https://www.abc.net.au/news/2021-08-18/hillsong-gay-conversion-therapy-practices-australia/100382352",
        "source_date": "2021-08-18",
        "incident_type": "conversion_practices",
        "date": "2010-01-01",  # Multiple incidents over years
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Multiple former Hillsong Church members reported being subjected to conversion practices. Survivors described being told their sexuality was sinful, encouraged to suppress their identity through prayer and counselling, and experiencing significant psychological harm as a result.",
        "severity": "high",
        "perpetrator_info": "Hillsong Church",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "cross_reference": "ABC News investigation"
    },
    {
        "title": "Exodus International conference - Brisbane survivor",
        "url": "https://www.abbi.org.au/conversion-therapy/",
        "source_date": "2000-01-01",
        "incident_type": "conversion_practices",
        "date": "1998-01-01",
        "location": "Brisbane, QLD",
        "victim_identity": "gay_man",
        "description": "Survivor subjected to Exodus International 'ex-gay' program and conferences in Brisbane. Exodus International was a major organization promoting conversion therapy globally before shutting down in 2013 and apologizing for harm caused.",
        "severity": "high",
        "perpetrator_info": "Exodus International ministry",
        "latitude": -27.4698,
        "longitude": 153.0251,
        "cross_reference": "ABBI; Exodus International (defunct 2013)"
    },
    {
        "title": "Youth conversion practices survivor - Perth",
        "url": "https://www.amnesty.org.au/what-are-conversion-practices/",
        "source_date": "2022-01-01",
        "incident_type": "conversion_practices",
        "date": "2019-01-01",
        "location": "Perth, WA",
        "victim_identity": "queer",
        "description": "Young person subjected to conversion practices in Western Australia, which lacks legal protections against such practices. Survivor experienced pressure from religious community to suppress their sexuality through prayer and pastoral counselling.",
        "severity": "high",
        "perpetrator_info": "Religious community in WA",
        "latitude": -31.9505,
        "longitude": 115.8605,
        "cross_reference": "Amnesty International Australia"
    },
]


def load_existing_incidents(filepath: str) -> List[Dict]:
    """Load existing incidents from CSV."""
    incidents = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                incidents.append(row)
    return incidents


def add_conversion_incidents(output_path: str = None) -> dict:
    """
    Add conversion practices incidents to the dataset.
    """
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, 'data', 'incidents_in_progress.csv')

    existing_incidents = load_existing_incidents(output_path)

    fieldnames = [
        'title', 'url', 'source_date', 'incident_type', 'date', 'location',
        'victim_identity', 'description', 'severity', 'perpetrator_info',
        'latitude', 'longitude', 'year_found', 'found_at', 'search_query',
        'cross_reference'
    ]

    added = 0
    new_incidents = []

    for case in CONVERSION_PRACTICES_INCIDENTS:
        # Check for duplicates by URL
        is_duplicate = any(
            inc.get('url', '') == case['url']
            for inc in existing_incidents
        )

        if is_duplicate:
            print(f"[SKIP] Already exists: {case['title'][:50]}...")
            continue

        incident = {
            'title': case['title'],
            'url': case['url'],
            'source_date': case.get('source_date', ''),
            'incident_type': case['incident_type'],
            'date': case['date'],
            'location': case['location'],
            'victim_identity': case['victim_identity'],
            'description': case['description'],
            'severity': case.get('severity', 'high'),
            'perpetrator_info': case.get('perpetrator_info', ''),
            'latitude': case['latitude'],
            'longitude': case['longitude'],
            'year_found': '',
            'found_at': datetime.now().isoformat(),
            'search_query': 'conversion_practices_scraper',
            'cross_reference': case.get('cross_reference', '')
        }
        new_incidents.append(incident)
        added += 1
        print(f"[ADDED] {case['title'][:60]}...")

    # Write all incidents
    all_incidents = existing_incidents + new_incidents

    # Ensure all incidents have cross_reference field
    for inc in all_incidents:
        if 'cross_reference' not in inc:
            inc['cross_reference'] = ''

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_incidents)

    print(f"\n=== Conversion Practices Integration Complete ===")
    print(f"Added: {added} new incidents")
    print(f"Total incidents in dataset: {len(all_incidents)}")

    return {
        'added': added,
        'total': len(all_incidents)
    }


if __name__ == "__main__":
    result = add_conversion_incidents()
    print(f"\nResult: {result}")
