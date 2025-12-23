"""
Populate state electoral divisions from GeoJSON files

Extracts division names from GeoJSON and creates initial MP data structure
"""

import json
from pathlib import Path
from generate_state_mp_voting_data import (
    STATE_BILLS, get_alignment_score, get_alignment_label, 
    get_alignment_color, build_voting_record, calculate_seat_alignment
)
from datetime import datetime

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

def create_sample_mp_data(state_code, division_name, bills):
    """Create sample MP data (to be replaced with real data)"""
    # Sample party distribution (will be replaced with real data)
    import random
    parties = ["Labor", "Liberal", "Greens", "Independent", "National", "LNP"]
    party = random.choice(parties)
    year_elected = random.randint(2018, 2023)
    
    voting_history = build_voting_record(state_code, bills, year_elected, party)
    current_mp_score = get_alignment_score(party, voting_history, year_elected)
    current_mp_years = 2025 - year_elected
    
    return {
        "state": state_code,
        "division_name": division_name,
        "current_mp": {
            "name": f"[MP Name - To Be Populated]",
            "party": party,
            "year_elected": year_elected,
            "alignment_score": current_mp_score,
            "alignment_label": get_alignment_label(current_mp_score),
            "alignment_color": get_alignment_color(current_mp_score),
            "note": "Sample data - requires real MP information from state parliament"
        },
        "previous_mps": [],
        "voting_history": voting_history,
        "data_period": {
            "start_year": 2010,
            "end_year": 2025,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "current_mp_period": f"{year_elected}-present"
        },
        "seat_alignment": {
            "score": current_mp_score,
            "label": get_alignment_label(current_mp_score),
            "color": get_alignment_color(current_mp_score),
            "calculation_period": "2010-2025",
            "description": "Weighted average of all MPs who held this seat since 2010"
        }
    }

def main():
    print("=" * 60)
    print("Populating State Electoral Divisions from GeoJSON")
    print("=" * 60)
    
    # Load existing structure
    with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    total_divisions = 0
    
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
            division_data = create_sample_mp_data(state_code, division_name, bills)
            divisions.append(division_data)
        
        dataset["states"][state_code]["divisions"] = divisions
        dataset["states"][state_code]["total_divisions"] = len(divisions)
        total_divisions += len(divisions)
        
        print(f"  Found {len(divisions)} divisions")
    
    # Update metadata
    dataset["metadata"]["total_divisions"] = total_divisions
    dataset["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # Save
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 60)
    print(f"Summary: {total_divisions} divisions across 8 states/territories")
    print(f"Output: {OUTPUT_PATH}")
    print(f"\nNOTE: MP names and voting records are sample data.")
    print("Next: Compile real MP data from state parliament websites")

if __name__ == "__main__":
    main()






