"""
Historical Commission Scraper

Integrates data from:
1. NSW Special Commission of Inquiry into LGBTIQ Hate Crimes (1970-2010)
2. Australian Institute of Criminology National Homicide Monitoring Program

These 88+ historical cases (1970-2010) provide crucial data on gay-hate
related murders and assaults that occurred before modern tracking systems.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

# Historical cases from NSW Special Commission and AIC research
# Source: https://lgbtiq.specialcommission.nsw.gov.au/
# Source: https://www.aic.gov.au/publications/tandi/tandi155

HISTORICAL_CASES = [
    # NSW Special Commission Cases (32 examined in detail)
    {
        "title": "Mark Stewart (Spanswick) - North Head death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1976-05-01",
        "incident_type": "murder",
        "date": "1976-05-01",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "18-year-old Mark Stewart was found at the base of cliffs at North Head, Manly. His death was ruled as multiple injuries from a fall, but the motive remains unclear and is suspected to be a gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Ernest Head - Summer Hill murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1976-06-01",
        "incident_type": "murder",
        "date": "1976-06-01",
        "location": "Summer Hill, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "44-year-old Ernest Head was murdered in his apartment, stabbed 35 times. NSW Special Commission arranged re-analysis of exhibits, identifying a known deceased male thought to be involved.",
        "severity": "critical",
        "perpetrator_info": "Known deceased male identified through palmprint analysis",
        "latitude": -33.8913,
        "longitude": 151.1374,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155"
    },
    {
        "title": "Barry Jones - Five Dock Park murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1976-09-26",
        "incident_type": "murder",
        "date": "1976-09-26",
        "location": "Five Dock Park, Five Dock, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old Barry Jones was found with 53 stab wounds and a 10cm throat laceration at Five Dock Park, a known gay beat location.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8694,
        "longitude": 151.1289,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Paul Rath - North Head death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1977-06-16",
        "incident_type": "murder",
        "date": "1977-06-16",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Paul Rath's body was found near the cliff base at North Head. Initially ruled accidental, but circumstances are suspicious and consistent with gay-hate violence.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "David Lloyd-Williams - North Head death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1978-08-24",
        "incident_type": "murder",
        "date": "1978-08-24",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "David Lloyd-Williams suffered severe depression and was found deceased at North Head. Case remains unsolved with suspected gay-hate motivation.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Walter John Bedser - Parramatta death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1980-12-01",
        "incident_type": "murder",
        "date": "1980-12-01",
        "location": "Parramatta, NSW",
        "victim_identity": "gay_man",
        "description": "Walter John Bedser, an antique dealer commonly called 'Johnny', was found deceased in Parramatta. Case remains unsolved.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8151,
        "longitude": 151.0011,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Richard Slater - Birdwood Park assault",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1980-12-22",
        "incident_type": "murder",
        "date": "1980-12-22",
        "location": "Birdwood Park, Newcastle, NSW",
        "victim_identity": "gay_man",
        "description": "69-year-old Richard Slater suffered severe head injuries from an attack at Birdwood Park, a known gay beat location in Newcastle. He died from his injuries at Newcastle Hospital.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -32.9267,
        "longitude": 151.7789,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Gerald Cuthbert - Paddington murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1981-10-18",
        "incident_type": "murder",
        "date": "1981-10-18",
        "location": "Paddington, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Gerald Cuthbert was stabbed over 60 times with his throat slit in his Paddington apartment. The extreme frenzied violence is characteristic of gay-hate crimes.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8847,
        "longitude": 151.2264,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Peter Sheil - Gordons Bay death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1983-04-01",
        "incident_type": "murder",
        "date": "1983-04-01",
        "location": "Gordons Bay, Clovelly, NSW",
        "victim_identity": "gay_man",
        "description": "29-year-old Peter Sheil's death circumstances at Gordons Bay/Clovelly cliffs remain unclear. He may have been pushed in a gay-hate attack.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9139,
        "longitude": 151.2639,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Peter Baumann - Waverley disappearance",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1983-10-26",
        "incident_type": "murder",
        "date": "1983-10-26",
        "location": "Waverley, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "25-year-old Peter Baumann, a German national, disappeared from Waverley/Double Bay area. His remains have never been found. The word 'AIDS' was written on a mirror, suggesting anti-gay motivation.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9000,
        "longitude": 151.2534,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Wendy Waine - Kings Cross murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1985-04-30",
        "incident_type": "murder",
        "date": "1985-04-30",
        "location": "Kings Cross, Sydney, NSW",
        "victim_identity": "trans_woman",
        "description": "Wendy Waine, a transgender woman and entertainer, was shot dead at close range in her Kings Cross apartment. This is a confirmed hate crime targeting her transgender identity.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8745,
        "longitude": 151.2232,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Gilles Mattaini - Marks Park disappearance",
        "url": "https://www.police.nsw.gov.au/can_you_help_us/rewards/100000_reward/deaths_of_gilles_mattaini,_ross_warren_and_john_russell",
        "source_date": "1985-09-15",
        "incident_type": "murder",
        "date": "1985-09-15",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Gilles Mattaini, a French national and barman at Menzies Hotel, went for a walk along the Tamarama coastal path and was never seen again. Coroner found he likely met similar fate to Ross Warren and John Russell at the same gay beat. $100,000 reward offered.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155; NSW Police $100k Reward"
    },
    {
        "title": "William Rooney - Wollongong death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1986-02-01",
        "incident_type": "murder",
        "date": "1986-02-01",
        "location": "Wollongong, NSW",
        "victim_identity": "gay_man",
        "description": "35-year-old William Rooney, originally from Scotland, suffered fatal facial and head injuries in Wollongong. Suspected gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -34.4278,
        "longitude": 150.8931,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "William Allen - Alexandria Park murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1988-12-28",
        "incident_type": "murder",
        "date": "1988-12-28",
        "location": "Alexandria Park, Alexandria, NSW",
        "victim_identity": "gay_man",
        "description": "48-year-old William Allen, a retired schoolteacher, was brutally bashed by a gang at Alexandria Park, a known gay beat location.",
        "severity": "critical",
        "perpetrator_info": "Gang of attackers",
        "latitude": -33.9067,
        "longitude": 151.1956,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Scott Johnson - North Head murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1988-12-10",
        "incident_type": "murder",
        "date": "1988-12-10",
        "location": "Blue Fish Point, North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Scott Johnson, an American mathematics PhD student at ANU, was found at the base of Blue Fish Point cliffs. Initially ruled suicide, but 2017 inquest determined he was a victim of a gay-hate attack. His brother Steve Johnson campaigned for decades for justice.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity at gay beat",
        "latitude": -33.8061,
        "longitude": 151.2936,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155"
    },
    {
        "title": "Andrew Currie - North Manly death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1988-12-01",
        "incident_type": "murder",
        "date": "1988-12-01",
        "location": "North Manly, NSW",
        "victim_identity": "gay_man",
        "description": "29-year-old Andrew Currie was found dead at a public toilet block in North Manly, a known gay beat location.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.7900,
        "longitude": 151.2800,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Russell Payne - Inverell death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1989-02-01",
        "incident_type": "murder",
        "date": "1989-02-01",
        "location": "Inverell, NSW",
        "victim_identity": "gay_man",
        "description": "33-year-old Russell Payne died at his home in Inverell. The case remains unsolved with suspected gay-hate motivation.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -29.7761,
        "longitude": 151.1133,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Samantha Raye - South Head death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1989-03-20",
        "incident_type": "murder",
        "date": "1989-03-20",
        "location": "Hornby Lighthouse, South Head, NSW",
        "victim_identity": "trans_woman",
        "description": "Samantha Raye, a transgender woman, was found in a coastal cave near Hornby Lighthouse at South Head. Suspected hate crime targeting her gender identity.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8322,
        "longitude": 151.2797,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "John Hughes - Potts Point murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1989-05-01",
        "incident_type": "murder",
        "date": "1989-05-01",
        "location": "Potts Point, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "45-year-old John Hughes was found bound with electrical cord, with a pillow sack over his head and multiple head injuries in his Potts Point apartment.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8704,
        "longitude": 151.2256,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Ross Warren - Marks Park disappearance",
        "url": "https://www.police.nsw.gov.au/can_you_help_us/rewards/100000_reward/deaths_of_gilles_mattaini,_ross_warren_and_john_russell",
        "source_date": "1989-07-22",
        "incident_type": "murder",
        "date": "1989-07-22",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "25-year-old Ross Warren, a television news reader for WIN Television, disappeared during a night out at Marks Park. His body was never recovered. Coroner found homicide 'probable'. Part of the 'Gay Gang Murders' at this notorious gay beat. $100,000 reward offered.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155; NSW Police $100k Reward"
    },
    {
        "title": "Graham Paynter - Tathra death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1989-10-13",
        "incident_type": "murder",
        "date": "1989-10-13",
        "location": "Tathra, NSW",
        "victim_identity": "gay_man",
        "description": "36-year-old Graham Paynter died in Tathra. The case remains unsolved with suspected gay-hate motivation.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -36.7303,
        "longitude": 149.9778,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "John Russell - Marks Park cliff death",
        "url": "https://www.police.nsw.gov.au/can_you_help_us/rewards/100000_reward/deaths_of_gilles_mattaini,_ross_warren_and_john_russell",
        "source_date": "1989-11-23",
        "incident_type": "murder",
        "date": "1989-11-23",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "31-year-old John Russell, an openly gay barman at Bronte Bowling Club, was last seen at his farewell drinks at Bondi Hotel. His battered body was found at the bottom of cliffs at Marks Park the next morning. 2005 inquest determined he was thrown from the cliff. Critical evidence (human hair in his hand) was lost by police. $100,000 reward offered.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155; NSW Police $100k Reward"
    },
    {
        "title": "Richard Johnson - Alexandria Park murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1990-01-01",
        "incident_type": "murder",
        "date": "1990-01-01",
        "location": "Alexandria Park, Alexandria, NSW",
        "victim_identity": "gay_man",
        "description": "Richard Johnson was beaten and kicked to death in a park toilet block at Alexandria Park. A gang of youths lured him to the toilet where he was bashed and stomped. Eight teens aged 16-18 were charged; three convicted of murder, five of manslaughter (known as 'Alexandria Eight').",
        "severity": "critical",
        "perpetrator_info": "Eight teenagers aged 16-18 (Alexandria Eight) - three convicted of murder, five of manslaughter",
        "latitude": -33.9067,
        "longitude": 151.1956,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155"
    },
    {
        "title": "Simon Blair Wark - Watson's Bay death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1990-01-10",
        "incident_type": "murder",
        "date": "1990-01-10",
        "location": "Watsons Bay, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Simon Blair Wark, an openly gay man, was last seen at Double Bay. His body was found floating off Manly cliffs days later.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8431,
        "longitude": 151.2789,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Kritchikorn Rattanajaturathaporn - Marks Park murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1990-07-15",
        "incident_type": "murder",
        "date": "1990-07-15",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "31-year-old Kritchikorn Rattanajaturathaporn, a Thai immigrant who arrived in Australia 4 months prior, was attacked with claw hammer, pipe and fists along with companion Geoffrey Sullivan at Marks Park. Kritchikorn was chased along the cliff edge with serious injuries, either pushed or lost footing, and fell to his death. Three men were convicted of assault and murder.",
        "severity": "critical",
        "perpetrator_info": "Three men convicted of assault and murder",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155"
    },
    {
        "title": "William Dutfield - Mosman death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1991-11-01",
        "incident_type": "murder",
        "date": "1991-11-01",
        "location": "Mosman, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old William Dutfield was found deceased in his Mosman apartment. The case remains unsolved with suspected gay-hate motivation.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8269,
        "longitude": 151.2466,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Robert Malcolm - Sydney GPO worker murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1992-01-01",
        "incident_type": "murder",
        "date": "1992-01-01",
        "location": "Eveleigh Street, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old Robert Malcolm, known as 'Bob', was a GPO worker who suffered complex skull fractures and severe head injuries in an attack near Eveleigh Street.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8950,
        "longitude": 151.1950,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Brian Walker - Merrylands death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1992-07-23",
        "incident_type": "murder",
        "date": "1992-07-23",
        "location": "Merrylands, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "30-year-old Brian Walker, described as a talented artist, was found deceased in Merrylands. Suspected gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8333,
        "longitude": 150.9917,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Crispin Dye - Oxford Street murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1993-12-23",
        "incident_type": "murder",
        "date": "1993-12-23",
        "location": "Oxford Street, Darlinghurst, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old Crispin Dye, manager for AC/DC, was found unconscious in a laneway behind Kinselas nightclub after a night out. He died in hospital on Christmas Day from multiple skull fractures. Critical evidence (blood-stained jeans and shirt) was never examined. NSW Special Commission found new DNA evidence identifying an unknown person of interest who died by suicide in 2002.",
        "severity": "critical",
        "perpetrator_info": "Person of interest identified via DNA (deceased, suicide 2002)",
        "latitude": -33.8778,
        "longitude": 151.2197,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes; AIC TANDI 155"
    },
    {
        "title": "James Meek - Surry Hills murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1995-03-07",
        "incident_type": "murder",
        "date": "1995-03-07",
        "location": "Northcott Flats, Surry Hills, NSW",
        "victim_identity": "gay_man",
        "description": "51-year-old James Meek was killed at his apartment in the Northcott Flats public housing complex in Surry Hills. Suspected gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8850,
        "longitude": 151.2150,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Kenneth Brennan - Elizabeth Bay murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1995-06-12",
        "incident_type": "murder",
        "date": "1995-06-12",
        "location": "Elizabeth Bay, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "53-year-old Kenneth Brennan, an openly gay history teacher, was last seen at a sauna before being stabbed multiple times. Fresh inquest recommended by Special Commission.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8700,
        "longitude": 151.2280,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Carl Stockton - Bar Cleveland murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1996-11-05",
        "incident_type": "murder",
        "date": "1996-11-05",
        "location": "Redfern, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "52-year-old Carl Stockton, a train driver, suffered massive head injuries with three separate impact areas at Bar Cleveland in Redfern. Suspected gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8933,
        "longitude": 151.2044,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Scott Miller - Millers Point death",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1997-03-02",
        "incident_type": "murder",
        "date": "1997-03-02",
        "location": "Millers Point, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "21-year-old Scott Miller, who grew up in Orange, was found at the base of a steep drop at Millers Point near Darling Harbour. Suspected gay-hate crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8578,
        "longitude": 151.2022,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Samantha Rose - Kensington murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "1997-12-22",
        "incident_type": "murder",
        "date": "1997-12-22",
        "location": "Kensington, Sydney, NSW",
        "victim_identity": "trans_woman",
        "description": "Samantha Rose, a transgender woman and Westpac computer analyst, was found with skull fractures from blunt force trauma in her Kensington home. Suspected hate crime targeting her transgender identity.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9133,
        "longitude": 151.2211,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    {
        "title": "Anthony Cawsey - Centennial Park murder",
        "url": "https://lgbtiq.specialcommission.nsw.gov.au/cases/",
        "source_date": "2009-09-26",
        "incident_type": "murder",
        "date": "2009-09-26",
        "location": "Centennial Park, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Anthony Cawsey, a charismatic stagehand, was found stabbed to death with a single stab wound to the chest at Centennial Park, a known gay beat area. He walked to the park in early morning hours from his Redfern flat. His pants were pulled down revealing pink women's underpants. Person of interest (Moses Kellie, age 24) was charged but case dismissed for lack of evidence. Kellie is now deceased.",
        "severity": "critical",
        "perpetrator_info": "Moses Kellie (deceased) - charges dismissed",
        "latitude": -33.8985,
        "longitude": 151.2353,
        "cross_reference": "NSW Special Commission of Inquiry into LGBTIQ Hate Crimes"
    },
    # George Duncan - Notable historical case
    {
        "title": "George Duncan - River Torrens murder",
        "url": "https://www.starobserver.com.au/news/murdered-gay-lecturer-george-duncan-honoured-by-university-of-adelaide/218636",
        "source_date": "1972-05-10",
        "incident_type": "murder",
        "date": "1972-05-10",
        "location": "River Torrens, Adelaide, SA",
        "victim_identity": "gay_man",
        "description": "George Duncan, a 41-year-old gay lecturer at the University of Adelaide, was thrown into the River Torrens and drowned. His murder led to significant law reform in South Australia, which became the first Australian state to decriminalize homosexuality in 1975. Members of the Vice Squad were suspected of involvement but never charged.",
        "severity": "critical",
        "perpetrator_info": "Members of SA Police Vice Squad suspected - never charged",
        "latitude": -34.9178,
        "longitude": 138.5917,
        "cross_reference": "AIC TANDI 155; University of Adelaide Memorial"
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


def _extract_victim_name(case: Dict) -> str:
    """Extract the victim's name from the title (before the first dash)."""
    title = case.get('title', '')
    if ' - ' in title:
        return title.split(' - ')[0].strip().lower()
    return title.strip().lower()


# Generic words to exclude from location matching (too common to be meaningful)
_LOCATION_STOPWORDS = {
    'nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act',
    'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide',
    'australia', 'new', 'south', 'wales', 'north', 'east', 'west',
}

# Generic words to exclude from description matching
_DESCRIPTION_STOPWORDS = {
    'found', 'death', 'killed', 'murder', 'attack', 'crime', 'victim',
    'unknown', 'suspected', 'police', 'investigation', 'years', 'known',
    'gay-hate', 'stabbed', 'injuries', 'their', 'about', 'after',
    'before', 'being', 'would', 'could', 'which', 'there', 'where',
    'while', 'other', 'still', 'never', 'under',
}


def find_duplicates(new_case: Dict, existing_incidents: List[Dict]) -> Optional[Dict]:
    """
    Find potential duplicates in existing data.
    Returns the matching incident if found, None otherwise.

    Uses victim name as a primary indicator. Falls back to a stricter
    2-of-3 criteria (date + location + description) with stopword
    filtering to avoid false positives on generic terms like 'NSW',
    'North', 'killed', etc.
    """
    new_date = new_case.get('date', '')
    new_location = new_case.get('location', '').lower()
    new_description = new_case.get('description', '').lower()
    new_name = _extract_victim_name(new_case)

    for incident in existing_incidents:
        existing_date = incident.get('date', '')
        existing_location = incident.get('location', '').lower()
        existing_description = incident.get('description', '').lower()
        existing_name = _extract_victim_name(incident)

        # Primary check: victim name match (strongest signal)
        name_match = False
        if new_name and existing_name:
            # Check if the full name matches, or surname matches
            new_parts = new_name.split()
            existing_parts = existing_name.split()
            # Full name match
            if new_name == existing_name:
                name_match = True
            # Surname match (last word) + at least one other part
            elif len(new_parts) >= 2 and len(existing_parts) >= 2:
                if new_parts[-1] == existing_parts[-1] and any(
                    p in existing_parts for p in new_parts[:-1]
                ):
                    name_match = True

        # If names match, it's almost certainly the same person
        if name_match:
            return incident

        # Check for date match (within same year for historical cases)
        date_match = False
        if new_date and existing_date:
            new_year = new_date[:4] if len(new_date) >= 4 else ''
            existing_year = existing_date[:4] if len(existing_date) >= 4 else ''
            date_match = new_year == existing_year

        # Check for location similarity (excluding generic stopwords)
        location_match = False
        if new_location and existing_location:
            new_words = set(new_location.replace(',', ' ').split()) - _LOCATION_STOPWORDS
            existing_words = set(existing_location.replace(',', ' ').split()) - _LOCATION_STOPWORDS
            common_words = new_words & existing_words
            if len(common_words) >= 2:
                location_match = True

        # Check for description similarity (excluding generic stopwords)
        desc_match = False
        if new_description and existing_description:
            new_words = set(
                w.strip('.,;:()') for w in new_description.split()
                if len(w) > 4
            ) - _DESCRIPTION_STOPWORDS
            existing_words = set(
                w.strip('.,;:()') for w in existing_description.split()
                if len(w) > 4
            ) - _DESCRIPTION_STOPWORDS
            common_words = new_words & existing_words
            if len(common_words) >= 4:
                desc_match = True

        # If at least 2 of 3 criteria match, consider it a duplicate
        matches = sum([date_match, location_match, desc_match])
        if matches >= 2:
            return incident

    return None


def add_historical_incidents(
    output_path: str = None,
    check_duplicates: bool = True
) -> dict:
    """
    Add historical incidents to the dataset.

    Returns:
        Dictionary with counts of added, duplicate, and updated incidents.
    """
    if output_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, 'data', 'incidents_in_progress.csv')

    # Load existing incidents
    existing_incidents = load_existing_incidents(output_path)

    added = 0
    duplicates = 0
    updated = 0

    fieldnames = [
        'title', 'url', 'source_date', 'incident_type', 'date', 'location',
        'victim_identity', 'description', 'severity', 'perpetrator_info',
        'latitude', 'longitude', 'year_found', 'found_at', 'search_query',
        'cross_reference'
    ]

    new_incidents = []

    for case in HISTORICAL_CASES:
        if check_duplicates:
            duplicate = find_duplicates(case, existing_incidents)
            if duplicate:
                # Add cross-reference to existing incident
                duplicates += 1
                print(f"[DUPLICATE] Found match for {case['title'][:50]}...")
                # We'll update the existing incident with cross-reference
                for i, inc in enumerate(existing_incidents):
                    if inc == duplicate:
                        cross_ref = case.get('cross_reference', '')
                        existing_cross_ref = inc.get('cross_reference', '')
                        if cross_ref and cross_ref not in existing_cross_ref:
                            inc['cross_reference'] = f"{existing_cross_ref}; {cross_ref}" if existing_cross_ref else cross_ref
                            updated += 1
                        break
                continue

        # Add new incident
        incident = {
            'title': case['title'],
            'url': case['url'],
            'source_date': case.get('source_date', ''),
            'incident_type': case['incident_type'],
            'date': case['date'],
            'location': case['location'],
            'victim_identity': case['victim_identity'],
            'description': case['description'],
            'severity': case.get('severity', 'critical'),
            'perpetrator_info': case.get('perpetrator_info', ''),
            'latitude': case['latitude'],
            'longitude': case['longitude'],
            'year_found': '',
            'found_at': datetime.now().isoformat(),
            'search_query': 'historical_commission_scraper',
            'cross_reference': case.get('cross_reference', '')
        }
        new_incidents.append(incident)
        added += 1
        print(f"[ADDED] {case['title'][:60]}...")

    # Write all incidents (existing + new) to file
    all_incidents = existing_incidents + new_incidents

    # Ensure all incidents have cross_reference field
    for inc in all_incidents:
        if 'cross_reference' not in inc:
            inc['cross_reference'] = ''

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_incidents)

    print(f"\n=== Historical Commission Integration Complete ===")
    print(f"Added: {added} new incidents")
    print(f"Duplicates found: {duplicates}")
    print(f"Updated with cross-references: {updated}")
    print(f"Total incidents in dataset: {len(all_incidents)}")

    return {
        'added': added,
        'duplicates': duplicates,
        'updated': updated,
        'total': len(all_incidents)
    }


if __name__ == "__main__":
    result = add_historical_incidents()
    print(f"\nResult: {result}")
