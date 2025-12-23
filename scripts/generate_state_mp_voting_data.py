"""
Generate State/Territory MP LGBTIQ+ Voting Records Database

Comprehensive voting records for all 8 states/territories on LGBTIQ+ legislation (2010-2025)

Data sources:
- State Parliament websites
- Hansard records
- Electoral Commission records
"""

import json
from datetime import datetime
from pathlib import Path

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "state-mp-lgbtiq-votes.json"

# State-specific bills tracked (2010-2025)
STATE_BILLS = {
    "NSW": [
        {
            "id": "conversion_practices_ban_2024",
            "name": "Conversion Practices Ban Act 2024",
            "short_name": "Conversion Practices Ban 2024",
            "year": 2024,
            "date": "2024-03-22",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Criminalized conversion practices. Took effect April 2025.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "equality_bill_amendments_2024",
            "name": "Equality Bill amendments (Alex Greenwich)",
            "short_name": "Equality Bill 2024",
            "year": 2024,
            "date": "2024-ongoing",
            "outcome": "Various amendments",
            "house": "Legislative Assembly",
            "description": "Anti-discrimination protections expansion",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "lgbtq_hate_crimes_inquiry_2024",
            "name": "LGBTQ hate crimes inquiry - Legislative response",
            "short_name": "Hate Crimes Inquiry 2024",
            "year": 2024,
            "date": "2024-ongoing",
            "outcome": "Recommendations implementation",
            "house": "Legislative Assembly",
            "description": "Special Commission of Inquiry recommendations",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        }
    ],
    "VIC": [
        {
            "id": "conversion_practices_ban_2020",
            "name": "Change or Suppression (Conversion) Practices Prohibition Bill 2020",
            "short_name": "Conversion Practices Ban 2020",
            "year": 2020,
            "date": "2020-11-26",
            "outcome": "Passed 55-0",
            "house": "Legislative Assembly",
            "description": "Most comprehensive conversion practices ban at the time. Fines up to $200,000 or 10 years jail. Took effect February 2022.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "gender_recognition_2019",
            "name": "Sex Discrimination Amendment Bill 2019 (Gender Recognition reforms)",
            "short_name": "Gender Recognition 2019",
            "year": 2019,
            "date": "2019",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Removed mandatory sexual reassignment surgery requirement. Allows self-nomination: male, female, or gender diverse/non-binary.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "gender_recognition_free_2023",
            "name": "Sex Discrimination Amendment Bill 2023 (Free gender recognition)",
            "short_name": "Free Gender Recognition 2023",
            "year": 2023,
            "date": "2023",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Removed all fees and costs for birth certificate changes (November 2025). First in Australia.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "equal_opportunity_amendments_2021",
            "name": "Equal Opportunity Act amendments 2021 (LGBTIQ+ protections expansion)",
            "short_name": "Equal Opportunity 2021",
            "year": 2021,
            "date": "2021",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Religious exceptions amendments, expanded LGBTIQ+ protections",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "lgbtiqa_commissioner",
            "name": "LGBTIQA+ Community Commissioner establishment",
            "short_name": "LGBTIQA+ Commissioner",
            "year": 2021,
            "date": "2021",
            "outcome": "Established",
            "house": "Legislative Assembly",
            "description": "First LGBTIQA+ Community Commissioner in Australia",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        }
    ],
    "QLD": [
        {
            "id": "conversion_practices_ban_2020",
            "name": "Health Legislation Amendment Bill 2019 - Conversion Practices Ban",
            "short_name": "Conversion Practices Ban 2020",
            "year": 2020,
            "date": "2020-03",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "FIRST jurisdiction nationwide to pass. Maximum penalty: 18 months imprisonment + fines. Queensland first globally for statutory conversion practices ban.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "anti_discrimination_2016",
            "name": "Anti-Discrimination Amendment (Sexual Orientation, Gender Identity and Intersex) Bill 2016",
            "short_name": "Anti-Discrimination 2016",
            "year": 2016,
            "date": "2016",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Comprehensive LGBTIQ+ protections",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "historical_convictions_2017",
            "name": "Criminal Law (Historical Convictions Expungement) Bill 2017",
            "short_name": "Conviction Expungement 2017",
            "year": 2017,
            "date": "2017",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Allows gay male homosexuality convictions to be expunged",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        },
        {
            "id": "gender_recognition_2018",
            "name": "Gender Recognition - Birth Certificate Changes (Divorce requirement repeal)",
            "short_name": "Gender Recognition 2018",
            "year": 2018,
            "date": "2018",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Repeal of divorce requirements for gender marker changes",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        },
        {
            "id": "gender_recognition_2024",
            "name": "Gender Recognition - Surgery requirement repeal 2024",
            "short_name": "Gender Recognition 2024",
            "year": 2024,
            "date": "2024",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Repeal of surgery requirements for gender marker changes",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "anti_discrimination_reform_2024",
            "name": "Anti-Discrimination Act Reform amendments 2024-2025",
            "short_name": "AD Act Reform 2024",
            "year": 2024,
            "date": "2024-2025",
            "outcome": "PAUSED indefinitely (March 2025)",
            "house": "Legislative Assembly",
            "description": "CRITICAL: Comprehensive reform package to modernise Anti-Discrimination Act (first update in 30 years). Originally due 1 July 2025. PAUSED indefinitely by government (March 2025). Would have strengthened protections across sectors.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3,
            "status": "paused"
        }
    ],
    "WA": [
        {
            "id": "conversion_practices_ban_pending",
            "name": "Conversion Practices Ban (PENDING)",
            "short_name": "Conversion Practices Ban",
            "year": 2025,
            "date": "2025-expected",
            "outcome": "PENDING - Expected after March 2025 election",
            "house": "Legislative Assembly",
            "description": "Committed 2022, delayed until after 2025 election (Sept 2024 decision). Will include criminal penalties + civil response scheme.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3,
            "status": "pending"
        },
        {
            "id": "gender_recognition_2024",
            "name": "Births, Deaths, Marriages Registration Amendment (Sex or Gender Changes) Bill 2024",
            "short_name": "Gender Recognition 2024",
            "year": 2024,
            "date": "2024",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Streamlined gender recognition process. Abolishes Gender Reassignment Board. No longer requires medical/surgical reassignment (clinical treatment now optional). Allows 'non-binary' sex descriptor.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "art_surrogacy_2025",
            "name": "Assisted Reproductive Technology and Surrogacy Bill 2025",
            "short_name": "ART & Surrogacy 2025",
            "year": 2025,
            "date": "2025-12",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Removes discriminatory barriers: same-sex couples, trans, intersex, single people can access ART/surrogacy. LGBTIQ+ family rights expansion.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "gay_conviction_expungement_2018",
            "name": "Gay Conviction Expungement Bill 2018",
            "short_name": "Conviction Expungement 2018",
            "year": 2018,
            "date": "2018",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Allows convictions for consensual gay sex (pre-1990) to be expunged",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        }
    ],
    "SA": [
        {
            "id": "conversion_practices_ban_2024",
            "name": "Conversion Practices Prohibition Act 2024",
            "short_name": "Conversion Practices Ban 2024",
            "year": 2024,
            "date": "2024-09",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "Took effect April 2025. Penalties: Up to 5 years jail for causing serious harm, 3 years for facilitation/arranging removal from state.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "gay_panic_defence_2020",
            "name": "Statutes Amendment (Abolition of Defence of Provocation and Related Matters) Act 2020",
            "short_name": "Gay Panic Defence Abolition 2020",
            "year": 2020,
            "date": "2020-11",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "Abolished gay panic defence",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "gender_recognition_2016",
            "name": "Birth, Deaths and Marriages Registration (Gender Identity) Amendment Act 2016",
            "short_name": "Gender Recognition 2016",
            "year": 2016,
            "date": "2016",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "Simpler gender recognition process. Removed surgery requirement.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "adoption_2016",
            "name": "Adoption (Review) Amendment Act 2016",
            "short_name": "Same-Sex Adoption 2016",
            "year": 2016,
            "date": "2016-12-07",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "Allowed same-sex couple adoption",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        },
        {
            "id": "historical_convictions_2012",
            "name": "Criminal Law (Historical Convictions Expungement) Act 2012",
            "short_name": "Conviction Expungement 2012",
            "year": 2012,
            "date": "2012",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "Gay male homosexuality convictions expunged",
            "pro_lgbtiq_vote": "Yes",
            "weight": 1
        }
    ],
    "TAS": [
        {
            "id": "conversion_practices_ban_pending",
            "name": "Conversion Practices Ban (PROPOSED)",
            "short_name": "Conversion Practices Ban",
            "year": 2025,
            "date": "2025-ongoing",
            "outcome": "PENDING - Under consideration",
            "house": "House of Assembly",
            "description": "Status: Under consideration. Get update when introduced/passed.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3,
            "status": "pending"
        },
        {
            "id": "gender_recognition_2019",
            "name": "Gender Recognition Act amendments 2019",
            "short_name": "Gender Recognition 2019",
            "year": 2019,
            "date": "2019-04",
            "outcome": "Passed",
            "house": "House of Assembly",
            "description": "MOST PROGRESSIVE gender-optional birth certificate laws in the world (2019). Removes forced divorce requirement. Removes sexual reassignment surgery requirement. Only requires simple declaration. Allows parents to choose gender on birth certificates. Allows removal of gender descriptor entirely. Lowers age for gender change without parental permission to 16. Includes non-binary gender option. Intersex children: extended time for birth registration (to 120 days).",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "historical_compensation_2025",
            "name": "Historical Convictions Compensation Scheme 2025",
            "short_name": "Compensation Scheme 2025",
            "year": 2025,
            "date": "2025-11",
            "outcome": "Implemented",
            "house": "House of Assembly",
            "description": "FIRST Australian compensation fund for past homosexuality & cross-dressing convictions. Covers pre-1997 (homosexuality) and pre-2002 (cross-dressing) convictions. Potentially 100+ individuals.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        }
    ],
    "ACT": [
        {
            "id": "gender_recognition_2024",
            "name": "Gender Recognition Bill / Equality Bill 2024",
            "short_name": "Gender Recognition 2024",
            "year": 2024,
            "date": "2024-03-21",
            "outcome": "Passed 12-5",
            "house": "Legislative Assembly",
            "description": "Removes clinical treatment requirement for gender recognition. Expands gender descriptors beyond male/female. Leading gender recognition reform.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3
        },
        {
            "id": "conversion_practices_ban_2024",
            "name": "ACT Conversion Practices Ban Bill 2023-2024",
            "short_name": "Conversion Practices Ban 2024",
            "year": 2024,
            "date": "2024",
            "outcome": "Status: GET DETAILS",
            "house": "Legislative Assembly",
            "description": "Conversion practices ban legislation",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3,
            "status": "pending"
        },
        {
            "id": "discrimination_amendments_2024",
            "name": "Discrimination Legislation Amendment Bill 2024",
            "short_name": "Discrimination Amendments 2024",
            "year": 2024,
            "date": "2024",
            "outcome": "Passed",
            "house": "Legislative Assembly",
            "description": "Anti-discrimination reforms",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        }
    ],
    "NT": [
        {
            "id": "conversion_practices_pending",
            "name": "Conversion Practices protections (PROPOSED)",
            "short_name": "Conversion Practices Ban",
            "year": 2025,
            "date": "2025-ongoing",
            "outcome": "PENDING - Under consideration",
            "house": "Legislative Assembly",
            "description": "Status: Not yet law. Get update when introduced/passed.",
            "pro_lgbtiq_vote": "Yes",
            "weight": 3,
            "status": "pending"
        },
        {
            "id": "anti_discrimination_2025",
            "name": "Anti-Discrimination Amendment Act 2025",
            "short_name": "Anti-Discrimination 2025",
            "year": 2025,
            "date": "2025-10-31",
            "outcome": "Assented",
            "house": "Legislative Assembly",
            "description": "LGBTIQ+ anti-discrimination protections. Part 3: Not yet commenced (note).",
            "pro_lgbtiq_vote": "Yes",
            "weight": 2
        }
    ]
}

# Party alignment baselines for state parliaments (similar to federal)
PARTY_ALIGNMENT = {
    "Greens": {"base_score": 100, "label": "Strong Supporter", "color": "#10b981"},
    "Labor": {"base_score": 90, "label": "Strong Supporter", "color": "#3b82f6"},
    "Independent": {"base_score": 75, "label": "Supporter", "color": "#6b7280"},
    "Liberal": {"base_score": 55, "label": "Mixed", "color": "#0ea5e9"},
    "LNP": {"base_score": 50, "label": "Mixed", "color": "#0ea5e9"},
    "National": {"base_score": 40, "label": "Mixed", "color": "#22c55e"},
    "One Nation": {"base_score": 5, "label": "Strong Opponent", "color": "#dc2626"},
    "KAP": {"base_score": 10, "label": "Strong Opponent", "color": "#ef4444"},
}

def get_alignment_score(party, votes, year_elected):
    """Calculate alignment score based on party and voting record"""
    base = PARTY_ALIGNMENT.get(party, {"base_score": 50})["base_score"]
    
    # Adjust based on voting record
    if votes:
        yes_votes = sum(1 for v in votes if v.get("vote") == "Yes")
        total_votes = len([v for v in votes if v.get("vote") in ["Yes", "No", "Abstained"]])
        if total_votes > 0:
            vote_ratio = yes_votes / total_votes
            # Adjust base score based on voting ratio
            if vote_ratio >= 0.8:
                base = min(100, base + 10)
            elif vote_ratio >= 0.6:
                base = min(100, base + 5)
            elif vote_ratio < 0.4:
                base = max(0, base - 20)
            elif vote_ratio < 0.2:
                base = max(0, base - 40)
    
    return min(100, max(0, round(base, 1)))

def get_alignment_label(score):
    """Get alignment label from score"""
    if score >= 75: return "Strong Supporter"
    if score >= 50: return "Supporter"
    if score >= 25: return "Mixed Record"
    return "Opponent"

def get_alignment_color(score):
    """Get color for alignment score"""
    if score >= 75: return "#10b981"  # Green
    if score >= 50: return "#3b82f6"  # Blue
    if score >= 25: return "#f59e0b"  # Amber
    return "#ef4444"  # Red

def calculate_seat_alignment(current_mp_score, current_mp_years, previous_mps_data):
    """Calculate seat-level alignment (weighted average)"""
    if not previous_mps_data:
        return current_mp_score
    
    total_years = current_mp_years
    weighted_sum = current_mp_score * current_mp_years
    
    for prev_mp in previous_mps_data:
        years_str = prev_mp.get("years_held", "")
        if "-" in years_str:
            try:
                start, end = years_str.split("-")
                years_held = int(end) - int(start)
                if years_held > 0:
                    total_years += years_held
                    weighted_sum += prev_mp["alignment_score"] * years_held
            except (ValueError, AttributeError):
                total_years += 3
                weighted_sum += prev_mp["alignment_score"] * 3
        else:
            total_years += 3
            weighted_sum += prev_mp["alignment_score"] * 3
    
    if total_years == 0:
        return current_mp_score
    
    return round(weighted_sum / total_years, 1)

def build_voting_record(state_code, bills, year_elected, party):
    """Build voting record for state bills"""
    records = []
    
    for bill in bills:
        # Skip pending bills if MP wasn't in office
        if bill.get("status") == "pending" and year_elected > bill["year"]:
            records.append({
                "bill_id": bill["id"],
                "bill_name": bill["name"],
                "short_name": bill["short_name"],
                "year": bill["year"],
                "vote": "N/A",
                "vote_display": "Not yet introduced",
                "bill_outcome": bill["outcome"],
                "pro_lgbtiq": None
            })
            continue
        
        # If MP wasn't in office when bill passed
        if year_elected > bill["year"]:
            records.append({
                "bill_id": bill["id"],
                "bill_name": bill["name"],
                "short_name": bill["short_name"],
                "year": bill["year"],
                "vote": "N/A",
                "vote_display": "Not in Parliament",
                "bill_outcome": bill["outcome"],
                "pro_lgbtiq": None
            })
            continue
        
        # Determine vote based on party (will be updated with actual voting records)
        if party in ["Labor", "Greens", "Independent"]:
            vote = "Yes"
            pro_lgbtiq = True
        elif party in ["Liberal", "LNP", "National"]:
            # Coalition MPs may have mixed records
            vote = "Yes" if bill.get("weight", 1) >= 3 else "Abstained"
            pro_lgbtiq = vote == "Yes"
        else:
            vote = "Unknown"
            pro_lgbtiq = None
        
        records.append({
            "bill_id": bill["id"],
            "bill_name": bill["name"],
            "short_name": bill["short_name"],
            "year": bill["year"],
            "vote": vote,
            "vote_display": vote,
            "bill_outcome": bill["outcome"],
            "pro_lgbtiq": pro_lgbtiq
        })
    
    return records

# NOTE: This is a template structure. Actual MP data will need to be compiled from state parliament records.
# For now, creating structure with sample data that can be populated.

def generate_sample_division(state_code, division_name, mp_name, party, year_elected, bills):
    """Generate sample division record (to be populated with real data)"""
    voting_history = build_voting_record(state_code, bills, year_elected, party)
    current_mp_score = get_alignment_score(party, voting_history, year_elected)
    current_mp_years = 2025 - year_elected
    
    record = {
        "state": state_code,
        "division_name": division_name,
        "current_mp": {
            "name": mp_name,
            "party": party,
            "year_elected": year_elected,
            "alignment_score": current_mp_score,
            "alignment_label": get_alignment_label(current_mp_score),
            "alignment_color": get_alignment_color(current_mp_score)
        },
        "previous_mps": [],
        "voting_history": voting_history,
        "data_period": {
            "start_year": 2010,
            "end_year": 2025,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "current_mp_period": f"{year_elected}-present"
        }
    }
    
    # Calculate seat alignment
    seat_alignment = calculate_seat_alignment(
        current_mp_score,
        current_mp_years,
        record["previous_mps"]
    )
    
    record["seat_alignment"] = {
        "score": seat_alignment,
        "label": get_alignment_label(seat_alignment),
        "color": get_alignment_color(seat_alignment),
        "calculation_period": "2010-2025",
        "description": "Weighted average of all MPs who held this seat since 2010"
    }
    
    return record

def main():
    print("=" * 60)
    print("Generating State/Territory MP LGBTIQ+ Voting Records Database")
    print("=" * 60)
    
    # This is a template structure. Real implementation requires:
    # 1. Compiling actual MP lists from state parliament websites
    # 2. Getting voting records from Hansard/parliament records
    # 3. Historical MP data from electoral archives
    
    # For now, create structure with metadata
    dataset = {
        "metadata": {
            "title": "Australian State/Territory MPs LGBTIQ+ Voting Records",
            "description": "Comprehensive voting records on LGBTIQ+ issues for all state and territory electoral divisions",
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "data_period": "2010-2025",
            "states_covered": list(STATE_BILLS.keys()),
            "sources": [
                {"name": "State Parliament Websites", "url": "Various"},
                {"name": "State Electoral Commissions", "url": "Various"},
                {"name": "Hansard Records", "url": "Various"}
            ],
            "methodology": {
                "description": "Alignment scores calculated from recorded parliamentary votes on LGBTIQ+ related legislation at state/territory level",
                "calculation": "(Pro-LGBTIQ+ votes / Total tracked votes) × Base party score adjustment",
                "score_ranges": {
                    "75-100": "Strong Supporter",
                    "50-74": "Supporter",
                    "25-49": "Mixed Record",
                    "0-24": "Opponent"
                },
                "note": "This is a template structure. Actual MP data and voting records need to be compiled from state parliament sources."
            },
            "disclaimer": "This tool presents objective voting records from state parliaments. We do not endorse any politician or party. Use this data to make informed decisions about who represents you."
        },
        "bills_by_state": STATE_BILLS,
        "states": {}
    }
    
    # Create structure for each state (to be populated with real data)
    for state_code, bills in STATE_BILLS.items():
        dataset["states"][state_code] = {
            "state_name": {
                "NSW": "New South Wales",
                "VIC": "Victoria",
                "QLD": "Queensland",
                "WA": "Western Australia",
                "SA": "South Australia",
                "TAS": "Tasmania",
                "ACT": "Australian Capital Territory",
                "NT": "Northern Territory"
            }[state_code],
            "house": "Legislative Assembly" if state_code != "SA" and state_code != "TAS" else "House of Assembly",
            "total_divisions": 0,  # Will be populated from GeoJSON
            "bills_tracked": len(bills),
            "divisions": []  # Will be populated with actual MP data
        }
    
    # Save structure
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated template structure")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nNOTE: This is a template. Next steps:")
    print("1. Compile actual MP lists from state parliament websites")
    print("2. Get voting records from Hansard/parliament records")
    print("3. Populate divisions array with real data")
    print("\nBills tracked by state:")
    for state_code, bills in STATE_BILLS.items():
        print(f"  {state_code}: {len(bills)} bills")

if __name__ == "__main__":
    main()

