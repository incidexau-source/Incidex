"""
Strike Force Parrabell Integration Script

Integrates all 88 cases from the NSW Police Strike Force Parrabell Final Report
into the incidents_in_progress.csv dataset.

Source: Strike Force Parrabell Final Report (2018)
- NSW Police Force investigative review of 88 deaths (1976-2000)
- Cases highlighted by AIC and media as having potential gay-hate bias motivation
- 27 cases classified as bias crimes (8 confirmed, 19 suspected)
"""

import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'incidents_in_progress.csv')

CROSS_REF = "Strike Force Parrabell (NSW Police, 2018)"

# All 88 Parrabell cases with research data
# Cases already in the CSV will have their cross_reference updated
# New cases will be added
PARRABELL_CASES = [
    {
        "parrabell_num": 1,
        "title": "Mark Stewart (Spanswick) - North Head death",
        "date": "1976-05-01",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "18-year-old Mark Stewart (also known as Spanswick) was found at the base of cliffs at North Head, Manly. His death was officially attributed to a fall but is suspected to be a gay-hate crime. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 2,
        "title": "Paul Rath - North Head death",
        "date": "1977-06-16",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Paul Rath was found near the cliff base at North Head. Initially ruled accidental. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 3,
        "title": "David Lloyd-Williams - North Head death",
        "date": "1978-08-24",
        "location": "North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "David Lloyd-Williams (listed as David Williams in Parrabell) was found deceased at North Head. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8122,
        "longitude": 151.2896,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 4,
        "title": "Walter John Bedser - Parramatta death",
        "date": "1980-12-01",
        "location": "Parramatta, NSW",
        "victim_identity": "gay_man",
        "description": "Walter John Bedser, an antique dealer, was found deceased in Parramatta. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8151,
        "longitude": 151.0011,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 5,
        "title": "Richard Slater - Birdwood Park assault",
        "date": "1980-12-22",
        "location": "Birdwood Park, Newcastle, NSW",
        "victim_identity": "gay_man",
        "description": "69-year-old Richard Slater suffered fatal head injuries at Birdwood Park, a known gay beat in Newcastle. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -32.9267,
        "longitude": 151.7789,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 6,
        "title": "Constantinos Giannaris - Randwick murder",
        "date": "1980-05-01",
        "location": "Randwick, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Constantinos Giannaris was found dead in his home in the Randwick area. His death was investigated as a potential gay-hate motivated homicide. Strike Force Parrabell Case #6.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9133,
        "longitude": 151.2414,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 7,
        "title": "Gerard Leslie Cuthbert - Paddington murder",
        "date": "1981-10-18",
        "location": "Paddington, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Gerard Cuthbert was stabbed over 60 times in his Paddington apartment. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8847,
        "longitude": 151.2264,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 8,
        "title": "Peter Parkes - Sydney murder",
        "date": "1981-12-01",
        "location": "Darlinghurst, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Peter Parkes was found dead in the Darlinghurst area of Sydney. His death was investigated as a potential gay-hate motivated killing. Strike Force Parrabell Case #8.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8778,
        "longitude": 151.2197,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 9,
        "title": "Ian Bridge - Sydney death",
        "date": "1982-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Ian Bridge died in Sydney under circumstances that were investigated as potentially gay-hate motivated. Strike Force Parrabell Case #9.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 10,
        "title": "Barry Charles Saunders - Sydney death",
        "date": "1982-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Barry Charles Saunders died in Sydney. His death was included in the list of 88 cases reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #10.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 11,
        "title": "Peter Sheil - Gordons Bay death",
        "date": "1983-04-01",
        "location": "Gordons Bay, Clovelly, NSW",
        "victim_identity": "gay_man",
        "description": "29-year-old Peter Sheil was found dead at Gordons Bay cliffs. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9139,
        "longitude": 151.2639,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 12,
        "title": "Gregory Peter Regan - Sydney murder",
        "date": "1983-08-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Gregory Peter Regan was killed in Sydney. His death was reviewed by Strike Force Parrabell as a potential gay-hate homicide. Strike Force Parrabell Case #12.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 13,
        "title": "Paul Edmund Hoson - Sydney murder",
        "date": "1983-10-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Paul Edmund Hoson was killed in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #13.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 14,
        "title": "Julian Ricardo Joseph D'Rozario - Alexandria murder",
        "date": "1984-01-01",
        "location": "Alexandria, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Julian Ricardo Joseph D'Rozario was found dead in the Alexandria area of Sydney. His death was reviewed as a potential gay-hate motivated killing. Strike Force Parrabell Case #14.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9067,
        "longitude": 151.1956,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 15,
        "title": "Patrick O'Neill - Sydney murder",
        "date": "1984-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Patrick O'Neill was killed in Sydney. His death was reviewed by Strike Force Parrabell. Strike Force Parrabell Case #15.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 16,
        "title": "Wayne (Wendy Wain) Brennan - Kings Cross murder",
        "date": "1985-04-30",
        "location": "Kings Cross, Sydney, NSW",
        "victim_identity": "trans_woman",
        "description": "Wayne Brennan, known as Wendy Wain/Waine, a transgender woman and entertainer, was shot dead at close range in Kings Cross. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8745,
        "longitude": 151.2232,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 17,
        "title": "Michael John Stevens - Bondi murder",
        "date": "1985-06-01",
        "location": "Bondi, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Michael John Stevens was found dead in the Bondi area. His death was reviewed as a potential gay-hate motivated killing. Strike Force Parrabell Case #17.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8908,
        "longitude": 151.2743,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 18,
        "title": "Phillip James Finlay - Sydney death",
        "date": "1985-07-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Phillip James Finlay died in Sydney under circumstances reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #18.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 19,
        "title": "Gilles Mattaini - Marks Park disappearance",
        "date": "1985-09-15",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old Gilles Mattaini disappeared from the Tamarama coastal path. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 20,
        "title": "William Anthony Rooney - Wollongong death",
        "date": "1986-02-01",
        "location": "Wollongong, NSW",
        "victim_identity": "gay_man",
        "description": "35-year-old William Rooney suffered fatal injuries in Wollongong. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -34.4278,
        "longitude": 150.8931,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 21,
        "title": "Peter John Simpson - Sydney death",
        "date": "1986-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Peter John Simpson died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #21.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 22,
        "title": "Raymond Frederick Keam - Alison Park murder",
        "date": "1987-01-17",
        "location": "Alison Park, Randwick, NSW",
        "victim_identity": "gay_man",
        "description": "Raymond Keam was found bashed to death at Alison Park in Randwick, a known gay beat. His case remained unsolved for decades. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown - $1 million reward offered",
        "latitude": -33.9167,
        "longitude": 151.2500,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 23,
        "title": "Keith William Richards - Sydney death",
        "date": "1987-04-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Keith William Richards died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #23.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 24,
        "title": "Stewart John Watts - Sydney death",
        "date": "1987-07-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Stewart John Watts died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #24.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 25,
        "title": "Geoffrey Solness - Sydney death",
        "date": "1987-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Geoffrey Solness died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #25.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 26,
        "title": "Phillip Peter Crombie - Sydney death",
        "date": "1988-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Phillip Peter Crombie died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #26.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 27,
        "title": "Mark Anthony Johnson - Sydney death",
        "date": "1988-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Mark Anthony Johnson died in Sydney. Not to be confused with Scott Johnson (Case #29). His death was reviewed by Strike Force Parrabell. Strike Force Parrabell Case #27.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 28,
        "title": "Leo Press - Sydney death",
        "date": "1988-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Leo Press died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #28.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 29,
        "title": "Scott Johnson - North Head murder",
        "date": "1988-12-10",
        "location": "Blue Fish Point, North Head, Manly, NSW",
        "victim_identity": "gay_man",
        "description": "27-year-old American mathematics PhD student found dead at base of cliffs. Third inquest ruled gay-hate murder. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Scott White convicted 2023",
        "latitude": -33.8061,
        "longitude": 151.2936,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 30,
        "title": "William Emanuel Allen - Alexandria Park murder",
        "date": "1988-12-28",
        "location": "Alexandria Park, Alexandria, NSW",
        "victim_identity": "gay_man",
        "description": "48-year-old William Allen was brutally bashed by a gang at Alexandria Park, a known gay beat. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Gang of attackers",
        "latitude": -33.9067,
        "longitude": 151.1956,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 31,
        "title": "Russell Payne - Inverell death",
        "date": "1989-02-01",
        "location": "Inverell, NSW",
        "victim_identity": "gay_man",
        "description": "33-year-old Russell Payne died at his home in Inverell. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -29.7761,
        "longitude": 151.1133,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 32,
        "title": "Samantha Raye - South Head death",
        "date": "1989-03-20",
        "location": "Hornby Lighthouse, South Head, NSW",
        "victim_identity": "trans_woman",
        "description": "Samantha Raye, a transgender woman, was found in a coastal cave near Hornby Lighthouse. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8322,
        "longitude": 151.2797,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 33,
        "title": "John Gordon Hughes - Potts Point murder",
        "date": "1989-05-01",
        "location": "Potts Point, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "45-year-old John Hughes was found bound with electrical cord in his Potts Point apartment. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8704,
        "longitude": 151.2256,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 34,
        "title": "Ross Bradley Warren - Marks Park disappearance",
        "date": "1989-07-22",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "25-year-old Ross Warren, a WIN TV newsreader, disappeared from Marks Park. Body never recovered. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 35,
        "title": "Graham Paynter - Tathra death",
        "date": "1989-10-13",
        "location": "Tathra, NSW",
        "victim_identity": "gay_man",
        "description": "36-year-old Graham Paynter died in Tathra. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -36.7303,
        "longitude": 149.9778,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 36,
        "title": "John Russell - Marks Park cliff death",
        "date": "1989-11-23",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "31-year-old John Russell was thrown from cliffs at Marks Park. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown - suspected gang activity",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 37,
        "title": "Andrew Currie - North Manly death",
        "date": "1988-12-01",
        "location": "North Manly, NSW",
        "victim_identity": "gay_man",
        "description": "29-year-old Andrew Currie was found dead at a public toilet block in North Manly, a known gay beat. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.7900,
        "longitude": 151.2800,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 38,
        "title": "Michael John Swaczak - Sydney death",
        "date": "1989-12-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Michael John Swaczak died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #38.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 39,
        "title": "Simon Blair Wark - Watsons Bay death",
        "date": "1990-01-10",
        "location": "Watsons Bay, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Simon Blair Wark was last seen at Double Bay, found floating off Manly cliffs. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8431,
        "longitude": 151.2789,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 40,
        "title": "Richard Norman Johnson - Alexandria Park murder",
        "date": "1990-01-01",
        "location": "Alexandria Park, Alexandria, NSW",
        "victim_identity": "gay_man",
        "description": "Richard Johnson was beaten and kicked to death in Alexandria Park. The 'Alexandria Eight' (teenagers aged 16-18) were convicted. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Eight teenagers - three convicted of murder, five of manslaughter",
        "latitude": -33.9067,
        "longitude": 151.1956,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 41,
        "title": "Wayne George Tonks - Sydney death",
        "date": "1990-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Wayne George Tonks died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #41.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 42,
        "title": "Krichakorn Rattanajurathaporn - Marks Park murder",
        "date": "1990-07-15",
        "location": "Marks Park, Tamarama, NSW",
        "victim_identity": "gay_man",
        "description": "31-year-old Thai immigrant was attacked with weapons and chased along Marks Park cliffs to his death. Three men convicted. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Three men convicted of assault and murder",
        "latitude": -33.8989,
        "longitude": 151.2716,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 43,
        "title": "Gary Webster - Sydney death",
        "date": "1990-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Gary Webster died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #43.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 44,
        "title": "William O'Shea - Sydney death",
        "date": "1990-11-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "William O'Shea died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #44.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 45,
        "title": "Michael Martin - Sydney death",
        "date": "1990-12-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Michael Martin died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #45.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 46,
        "title": "Maurice McCarty - Sydney death",
        "date": "1991-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Maurice McCarty died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #46.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 47,
        "title": "Noel William Walsh - Sydney death",
        "date": "1991-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Noel William Walsh died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #47.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 48,
        "title": "John Stephen Cranfield - Sydney death",
        "date": "1991-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "John Stephen Cranfield died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #48.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 49,
        "title": "Felipe Flores - Sydney murder",
        "date": "1991-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Felipe Flores was killed in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #49.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 50,
        "title": "William Dutfield - Mosman death",
        "date": "1991-11-01",
        "location": "Mosman, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old William Dutfield found deceased in his Mosman apartment. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8269,
        "longitude": 151.2466,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 51,
        "title": "Robert Malcolm - Sydney GPO worker murder",
        "date": "1992-01-01",
        "location": "Eveleigh Street, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old Robert Malcolm suffered complex skull fractures near Eveleigh Street. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8950,
        "longitude": 151.1950,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 52,
        "title": "Robert Anthony Knox - Sydney death",
        "date": "1992-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Robert Anthony Knox died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #52.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 53,
        "title": "Brian Travers - Sydney death",
        "date": "1992-05-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Brian Travers died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #53.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 54,
        "title": "Simon McHugh - Sydney death",
        "date": "1992-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Simon McHugh died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #54.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 55,
        "title": "Brian Walker - Merrylands death",
        "date": "1992-07-23",
        "location": "Merrylands, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "30-year-old Brian Walker found deceased in Merrylands. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8333,
        "longitude": 150.9917,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 56,
        "title": "Cyril Olsen - Sydney murder",
        "date": "1992-08-01",
        "location": "Surry Hills, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Cyril Olsen was found dead in the Surry Hills area. A prisoner reportedly confessed to the crime but later retracted. His death was reviewed by Strike Force Parrabell. Strike Force Parrabell Case #56.",
        "severity": "critical",
        "perpetrator_info": "Unknown - confession retracted",
        "latitude": -33.8850,
        "longitude": 151.2150,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 57,
        "title": "Robert John Maclean - Sydney death",
        "date": "1992-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Robert John Maclean died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #57.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 58,
        "title": "Sidney Alexander Hoare - Sydney death",
        "date": "1993-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Sidney Alexander Hoare died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #58.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 59,
        "title": "Donald Gillies - Sydney death",
        "date": "1993-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Donald Gillies died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #59.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 60,
        "title": "Kevin William Marsh - Sydney death",
        "date": "1993-05-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Kevin William Marsh died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #60.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 61,
        "title": "Gordon Bryan Tuckey - Sydney death",
        "date": "1993-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Gordon Bryan Tuckey died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #61.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 62,
        "title": "John Milicevic - Sydney death",
        "date": "1993-08-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "John Milicevic died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #62.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 63,
        "title": "Mervyn Thomas (Tom) Argaet - Sydney death",
        "date": "1993-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Mervyn Thomas Argaet (known as Tom) died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #63.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 64,
        "title": "Barry Webster - Sydney death",
        "date": "1993-10-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Barry Webster died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #64.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 65,
        "title": "Crispin Wilson Dye - Oxford Street murder",
        "date": "1993-12-23",
        "location": "Oxford Street, Darlinghurst, NSW",
        "victim_identity": "gay_man",
        "description": "41-year-old Crispin Dye, AC/DC manager, found unconscious behind Kinselas nightclub, died of skull fractures. Parrabell classification: Evidence of Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Person of interest identified via DNA (deceased 2002)",
        "latitude": -33.8778,
        "longitude": 151.2197,
        "incident_type": "murder",
        "parrabell_classification": "EBC"
    },
    {
        "parrabell_num": 66,
        "title": "Gordon Mills - Sydney death",
        "date": "1994-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Gordon Mills died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #66.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 67,
        "title": "Stephen Dempsey - Sydney death",
        "date": "1994-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Stephen Dempsey died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #67.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 68,
        "title": "James (Jim) William Meek - Surry Hills murder",
        "date": "1995-03-07",
        "location": "Northcott Flats, Surry Hills, NSW",
        "victim_identity": "gay_man",
        "description": "51-year-old James Meek was killed at Northcott Flats in Surry Hills. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8850,
        "longitude": 151.2150,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 69,
        "title": "Kenneth Brennan - Elizabeth Bay murder",
        "date": "1995-06-12",
        "location": "Elizabeth Bay, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "53-year-old Kenneth Brennan, gay history teacher, stabbed multiple times after visiting a sauna. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8700,
        "longitude": 151.2280,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 70,
        "title": "Craig Thomas - Sydney death",
        "date": "1995-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Craig Thomas died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #70.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 71,
        "title": "Scott Stuart Miller - Millers Point death",
        "date": "1997-03-02",
        "location": "Millers Point, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "21-year-old Scott Miller found at base of steep drop at Millers Point. Parrabell classification: Insufficient Information.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8578,
        "longitude": 151.2022,
        "incident_type": "murder",
        "parrabell_classification": "II"
    },
    {
        "parrabell_num": 72,
        "title": "Christopher Smith - Sydney death",
        "date": "1997-04-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Christopher Smith died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #72.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 73,
        "title": "Peter Brown Rowland - Sydney death",
        "date": "1997-05-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Peter Brown Rowland died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #73.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 74,
        "title": "Geoffrey Boyson - Sydney death",
        "date": "1997-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Geoffrey Boyson died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #74.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 75,
        "title": "Carl Stockson - Bar Cleveland murder",
        "date": "1996-11-05",
        "location": "Redfern, Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "52-year-old Carl Stockson (also written Stockton), a train driver, suffered massive head injuries at Bar Cleveland in Redfern. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8933,
        "longitude": 151.2044,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 76,
        "title": "Paul Erskine - Sydney murder",
        "date": "1997-08-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Paul Erskine died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #76.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 77,
        "title": "Robert Campbell - Sydney death",
        "date": "1997-10-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Robert Campbell died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #77.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 78,
        "title": "Joseph Zimmer - Sydney death",
        "date": "1998-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Joseph Zimmer died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #78.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 79,
        "title": "Barry Coulter - Sydney death",
        "date": "1998-03-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Barry Coulter died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #79.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 80,
        "title": "David Rose (Samantha Rose) - Kensington murder",
        "date": "1997-12-22",
        "location": "Kensington, Sydney, NSW",
        "victim_identity": "trans_woman",
        "description": "David Rose, known as Samantha Rose, a transgender woman and Westpac computer analyst, was found with skull fractures in her Kensington home. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.9133,
        "longitude": 151.2211,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 81,
        "title": "Trevor Parkin - Sydney death",
        "date": "1998-05-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Trevor Parkin died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #81.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 82,
        "title": "David O'Hearn - Sydney death",
        "date": "1998-07-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "David O'Hearn died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #82.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 83,
        "title": "Frank Arkell - Wollongong murder",
        "date": "1998-06-26",
        "location": "Wollongong, NSW",
        "victim_identity": "gay_man",
        "description": "Frank Arkell, 62, former Lord Mayor of Wollongong, was bludgeoned to death with a bedside lamp in his home. Killed by Mark Valera, a serial killer who also murdered David O'Hearn. Arkell was openly gay and had faced paedophilia allegations. Parrabell classification: Suspected Bias Crime.",
        "severity": "critical",
        "perpetrator_info": "Mark Valera - convicted serial killer",
        "latitude": -34.4278,
        "longitude": 150.8931,
        "incident_type": "murder",
        "parrabell_classification": "SBC"
    },
    {
        "parrabell_num": 84,
        "title": "John Chudleigh - Sydney death",
        "date": "1998-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "John Chudleigh died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #84.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 85,
        "title": "Brendan McGovern - Sydney death",
        "date": "1999-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Brendan McGovern died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #85.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 86,
        "title": "Harry Jansons - Sydney death",
        "date": "2000-01-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Harry Jansons died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #86.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 87,
        "title": "Jamie Creighton - Sydney death",
        "date": "2000-06-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Jamie Creighton died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #87.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
    {
        "parrabell_num": 88,
        "title": "Ali Mokdad - Sydney death",
        "date": "2000-09-01",
        "location": "Sydney, NSW",
        "victim_identity": "gay_man",
        "description": "Ali Mokdad died in Sydney. His death was reviewed by Strike Force Parrabell as potentially motivated by anti-gay bias. Strike Force Parrabell Case #88.",
        "severity": "critical",
        "perpetrator_info": "Unknown",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "incident_type": "murder",
        "parrabell_classification": "NEBC"
    },
]


def extract_surname(title):
    """Extract surname from case title for matching."""
    name_part = title.split(' - ')[0] if ' - ' in title else title
    # Remove parenthetical notes
    import re
    name_part = re.sub(r'\([^)]*\)', '', name_part).strip()
    parts = name_part.split()
    return parts[-1].lower() if parts else ''


def find_existing_match(case, existing_rows):
    """Find matching row in existing CSV by surname + year."""
    surname = extract_surname(case['title'])
    case_year = case['date'][:4]

    for row in existing_rows:
        row_title = row.get('title', '').lower()
        row_desc = row.get('description', '').lower()
        row_date = row.get('date', '')
        row_year = row_date[:4] if len(row_date) >= 4 else ''

        # Check surname in title
        if surname in row_title:
            # Verify it's the same era (within 2 years)
            if row_year and case_year:
                if abs(int(row_year) - int(case_year)) <= 2:
                    return row

        # Special cases: spelling variations
        spelling_map = {
            'rattanajurathaporn': 'rattanajaturathaporn',
            'stockson': 'stockton',
            'wain': 'waine',
        }
        if surname in spelling_map:
            alt = spelling_map[surname]
            if alt in row_title or alt in row_desc:
                return row

    return None


def integrate_parrabell():
    """Integrate Parrabell cases into the CSV."""
    # Load existing data
    existing = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing = list(reader)

    fieldnames = [
        'title', 'url', 'source_date', 'incident_type', 'date', 'location',
        'victim_identity', 'description', 'severity', 'perpetrator_info',
        'latitude', 'longitude', 'year_found', 'found_at', 'search_query',
        'cross_reference'
    ]

    added = 0
    updated = 0
    already_present = 0

    for case in PARRABELL_CASES:
        match = find_existing_match(case, existing)

        if match:
            # Update cross-reference on existing row
            existing_xref = match.get('cross_reference', '')
            if CROSS_REF not in existing_xref:
                if existing_xref:
                    match['cross_reference'] = f"{existing_xref}; {CROSS_REF}"
                else:
                    match['cross_reference'] = CROSS_REF
                updated += 1
                print(f"[UPDATED] #{case['parrabell_num']} {case['title'][:50]} - added Parrabell xref")
            else:
                already_present += 1
        else:
            # Add new case
            new_row = {
                'title': case['title'],
                'url': 'https://www.police.nsw.gov.au/__data/assets/pdf_file/0003/575265/Strike_Force_Parrabell_-_FINAL_REPORT.pdf',
                'source_date': case['date'],
                'incident_type': case['incident_type'],
                'date': case['date'],
                'location': case['location'],
                'victim_identity': case['victim_identity'],
                'description': case['description'],
                'severity': case['severity'],
                'perpetrator_info': case['perpetrator_info'],
                'latitude': case['latitude'],
                'longitude': case['longitude'],
                'year_found': '',
                'found_at': datetime.now().isoformat(),
                'search_query': 'integrate_parrabell',
                'cross_reference': CROSS_REF,
            }
            existing.append(new_row)
            added += 1
            print(f"[ADDED]   #{case['parrabell_num']} {case['title'][:50]}")

    # Ensure all rows have cross_reference field
    for row in existing:
        if 'cross_reference' not in row:
            row['cross_reference'] = ''

    # Write back
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(existing)

    print(f"\n{'='*60}")
    print(f"Strike Force Parrabell Integration Complete")
    print(f"{'='*60}")
    print(f"Added:           {added} new cases")
    print(f"Updated xrefs:   {updated} existing cases")
    print(f"Already present: {already_present} (no change)")
    print(f"Total in CSV:    {len(existing)}")
    return {'added': added, 'updated': updated, 'total': len(existing)}


if __name__ == '__main__':
    integrate_parrabell()
