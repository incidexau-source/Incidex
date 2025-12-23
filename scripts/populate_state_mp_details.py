"""
Populate State/Territory MP Details

This script populates the state-mp-lgbtiq-votes.json file with MP details
for all state and territory electoral divisions.

Data sources to be used:
- State parliament websites for current MPs
- Electoral Commission records for historical MPs
- Hansard for voting records

For now, creates realistic sample data based on typical state election patterns.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from generate_state_mp_voting_data import (
    STATE_BILLS, get_alignment_score, get_alignment_label, 
    get_alignment_color, build_voting_record, calculate_seat_alignment,
    PARTY_ALIGNMENT
)

GEOJSON_DIR = Path(__file__).parent.parent / "data" / "state-electoral-divisions"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "state-mp-lgbtiq-votes.json"

# Property name mappings for different states' GeoJSON formats
PROPERTY_MAPPINGS = {
    "NSW": ["Elect_div", "E_div_numb", "NAME", "name"],
    "VIC": ["Elect_div", "E_div_numb", "NAME", "name"],
    "QLD": ["Elect_div", "E_div_numb", "NAME", "name"],
    "WA": ["Elect_div", "E_div_numb", "NAME", "name"],
    "SA": ["Elect_div", "E_div_numb", "NAME", "name"],
    "TAS": ["Elect_div", "E_div_numb", "NAME", "name"],
    "ACT": ["Elect_div", "E_div_numb", "NAME", "name"],
    "NT": ["Elect_div", "E_div_numb", "NAME", "name"],
}

# Typical party distributions by state (based on recent election results)
# Format: {state: [(party, probability_weight), ...]}
STATE_PARTY_DISTRIBUTIONS = {
    "NSW": [
        ("Labor", 0.40),
        ("Liberal", 0.35),
        ("National", 0.10),
        ("Greens", 0.08),
        ("Independent", 0.07),
    ],
    "VIC": [
        ("Labor", 0.45),
        ("Liberal", 0.30),
        ("Greens", 0.10),
        ("Independent", 0.10),
        ("National", 0.05),
    ],
    "QLD": [
        ("Labor", 0.35),
        ("LNP", 0.40),
        ("Greens", 0.08),
        ("KAP", 0.05),
        ("Independent", 0.12),
    ],
    "WA": [
        ("Labor", 0.50),
        ("Liberal", 0.30),
        ("National", 0.08),
        ("Greens", 0.07),
        ("Independent", 0.05),
    ],
    "SA": [
        ("Labor", 0.45),
        ("Liberal", 0.35),
        ("Independent", 0.12),
        ("Greens", 0.08),
    ],
    "TAS": [
        ("Labor", 0.40),
        ("Liberal", 0.40),
        ("Greens", 0.12),
        ("Independent", 0.08),
    ],
    "ACT": [
        ("Labor", 0.50),
        ("Liberal", 0.30),
        ("Greens", 0.15),
        ("Independent", 0.05),
    ],
    "NT": [
        ("Labor", 0.55),
        ("Country Liberal", 0.35),
        ("Independent", 0.10),
    ],
}

# Sample first and last names for generating placeholder MP names
FIRST_NAMES = [
    "Alex", "Jordan", "Sam", "Taylor", "Casey", "Morgan", "Riley", "Avery",
    "Cameron", "Dakota", "Jamie", "Quinn", "Sage", "Blake", "Drew", "Finley",
    "Harper", "Hayden", "Kai", "Logan", "Noah", "Parker", "Reese", "River",
    "Rowan", "Skylar", "Tatum", "Tyler", "Zion", "Adrian", "Blair", "Dale",
    "Dana", "Drew", "Eden", "Emery", "Finley", "Gray", "Hayden", "Jules",
    "Kendall", "Lane", "Lennox", "Marley", "Micah", "Nico", "Peyton", "Quinn",
    "Reese", "Remy", "Rory", "Sage", "Shiloh", "Skylar", "Tatum", "Tyler"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans",
    "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart"
]

def weighted_choice(choices):
    """Select a party based on weighted probabilities"""
    parties, weights = zip(*choices)
    return random.choices(parties, weights=weights, k=1)[0]

def generate_mp_name():
    """Generate a placeholder MP name"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def get_division_name(feature, state_code):
    """Extract division name from GeoJSON feature"""
    props = feature.get("properties", {})
    
    for prop_name in PROPERTY_MAPPINGS.get(state_code, ["Elect_div", "NAME", "name"]):
        if prop_name in props and props[prop_name]:
            return str(props[prop_name]).strip()
    
    return f"Unknown Division {feature.get('id', '')}"

def load_geojson(state_code):
    """Load GeoJSON file for a state"""
    geojson_path = GEOJSON_DIR / f"{state_code.lower()}.geojson"
    
    if not geojson_path.exists():
        return None
    
    try:
        with open(geojson_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {geojson_path}: {e}")
        return None

def create_mp_data(state_code, division_name, bills):
    """Create MP data for a division"""
    # Select party based on state distribution
    party_dist = STATE_PARTY_DISTRIBUTIONS.get(state_code, [("Labor", 0.5), ("Liberal", 0.5)])
    party = weighted_choice(party_dist)
    
    # Generate election year (typically 2019, 2020, 2021, 2022, 2023, or 2024)
    # State elections vary, but most recent would be 2022-2024
    election_years = {
        "NSW": [2023, 2019, 2015],
        "VIC": [2022, 2018, 2014],
        "QLD": [2024, 2020, 2017],
        "WA": [2025, 2021, 2017],
        "SA": [2022, 2018, 2014],
        "TAS": [2024, 2021, 2018],
        "ACT": [2024, 2020, 2016],
        "NT": [2024, 2020, 2016],
    }
    year_elected = random.choice(election_years.get(state_code, [2022, 2020, 2018]))
    
    # Generate MP name
    mp_name = generate_mp_name()
    
    # Build voting record
    voting_history = build_voting_record(state_code, bills, year_elected, party)
    
    # Calculate alignment scores
    current_mp_score = get_alignment_score(party, voting_history, year_elected)
    current_mp_years = 2025 - year_elected
    
    # Create previous MP (if applicable - 30% chance)
    previous_mps = []
    if random.random() < 0.3 and year_elected > 2015:
        prev_year = year_elected - random.randint(3, 6)
        prev_party = weighted_choice(party_dist)
        prev_voting_history = build_voting_record(state_code, bills, prev_year, prev_party)
        prev_score = get_alignment_score(prev_party, prev_voting_history, prev_year)
        
        previous_mps.append({
            "name": generate_mp_name(),
            "party": prev_party,
            "years_held": f"{prev_year}-{year_elected}",
            "alignment_score": prev_score,
            "alignment_label": get_alignment_label(prev_score),
            "alignment_color": get_alignment_color(prev_score)
        })
    
    # Calculate seat alignment (weighted average)
    seat_alignment = calculate_seat_alignment(
        current_mp_score,
        current_mp_years,
        previous_mps
    )
    
    return {
        "state": state_code,
        "division_name": division_name,
        "current_mp": {
            "name": mp_name,
            "party": party,
            "year_elected": year_elected,
            "alignment_score": current_mp_score,
            "alignment_label": get_alignment_label(current_mp_score),
            "alignment_color": get_alignment_color(current_mp_score),
            "current_mp_alignment": {
                "score": current_mp_score,
                "label": get_alignment_label(current_mp_score),
                "description": f"Current MP's personal voting record ({year_elected}-present)"
            }
        },
        "previous_mps": previous_mps,
        "voting_history": voting_history,
        "seat_alignment": {
            "score": seat_alignment,
            "label": get_alignment_label(seat_alignment),
            "color": get_alignment_color(seat_alignment),
            "calculation_period": "2010-2025",
            "description": "Weighted average of all MPs who held this seat since 2010"
        },
        "data_period": {
            "start_year": 2010,
            "end_year": 2025,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "current_mp_period": f"{year_elected}-present"
        },
        "data_status": "populated",
        "data_note": "MP names and details are generated based on typical state election patterns. Real data should be compiled from state parliament websites."
    }

def main():
    print("=" * 70)
    print("Populating State/Territory MP Details")
    print("=" * 70)
    
    # Load existing structure
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    total_divisions = 0
    
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    # Process each state
    for state_code in STATE_BILLS.keys():
        print(f"\nProcessing {state_code}...")
        
        geojson = load_geojson(state_code)
        if not geojson:
            print(f"  ERROR: Could not load GeoJSON for {state_code}")
            continue
        
        features = geojson.get("features", [])
        bills = STATE_BILLS[state_code]
        divisions = []
        
        for feature in features:
            division_name = get_division_name(feature, state_code)
            division_data = create_mp_data(state_code, division_name, bills)
            divisions.append(division_data)
        
        dataset["states"][state_code]["divisions"] = divisions
        dataset["states"][state_code]["total_divisions"] = len(divisions)
        total_divisions += len(divisions)
        
        print(f"  [OK] Populated {len(divisions)} divisions")
        print(f"    Parties: {', '.join(set(d['current_mp']['party'] for d in divisions))}")
    
    # Update metadata
    dataset["metadata"]["total_divisions"] = total_divisions
    dataset["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    dataset["metadata"]["data_status"] = "populated_with_sample_data"
    dataset["metadata"]["data_note"] = "MP details populated with realistic sample data based on typical state election patterns. Real MP names and voting records should be compiled from state parliament sources."
    
    # Save
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 70)
    print(f"[SUCCESS] Successfully populated {total_divisions} divisions across 8 states/territories")
    print(f"  Output: {OUTPUT_PATH}")
    print(f"\nNOTE: This is sample data based on typical election patterns.")
    print("      Real MP names and voting records should be compiled from:")
    print("      - State parliament websites")
    print("      - Electoral Commission records")
    print("      - Hansard voting records")
    print("=" * 70)

if __name__ == "__main__":
    main()

