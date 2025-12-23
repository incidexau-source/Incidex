"""
Validate Electoral Divisions GeoJSON

Run this after converting your shapefile to GeoJSON to ensure
it's ready for use in the Leaflet map.

Usage: python scripts/validate_electoral_geojson.py
"""

import json
import os
from pathlib import Path

# Configuration
GEOJSON_PATH = Path(__file__).parent.parent / "data" / "electoral-divisions.geojson"

# Australia bounding box (rough)
AU_BOUNDS = {
    "min_lon": 112.0,
    "max_lon": 154.0,
    "min_lat": -44.0,
    "max_lat": -10.0
}

# Expected number of federal electoral divisions (2024 redistribution)
EXPECTED_DIVISIONS = 151


def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def get_nested_coords(geometry):
    """Extract all coordinates from any geometry type"""
    coords = []
    
    def extract(obj):
        if isinstance(obj, list):
            if len(obj) >= 2 and all(isinstance(x, (int, float)) for x in obj[:2]):
                # This is a coordinate pair [lon, lat]
                coords.append(obj)
            else:
                for item in obj:
                    extract(item)
    
    if geometry and 'coordinates' in geometry:
        extract(geometry['coordinates'])
    
    return coords


def validate_geojson():
    """Main validation function"""
    print("=" * 60)
    print("Electoral Divisions GeoJSON Validator")
    print("=" * 60)
    print()
    
    # Check file exists
    if not GEOJSON_PATH.exists():
        print(f"[ERROR] File not found at {GEOJSON_PATH}")
        print("\nPlease ensure you've saved the GeoJSON file to:")
        print(f"   {GEOJSON_PATH}")
        return False
    
    # Check file size
    file_size = GEOJSON_PATH.stat().st_size
    print(f"File: {GEOJSON_PATH.name}")
    print(f"Size: {format_size(file_size)}")
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        print("[WARNING] File is large (>10MB). Consider simplifying geometry.")
        print("   Tip: Use mapshaper.org to simplify to 10-15%")
    elif file_size > 5 * 1024 * 1024:  # 5MB
        print("[NOTE] File is moderately large. Map may load slowly.")
    else:
        print("[OK] File size is good for web use")
    
    print()
    
    # Load and parse JSON
    try:
        with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("[OK] Valid JSON format")
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Could not read file - {e}")
        return False
    
    # Check GeoJSON structure
    if data.get('type') != 'FeatureCollection':
        print(f"[ERROR] Expected FeatureCollection, got {data.get('type')}")
        return False
    print("[OK] Valid GeoJSON FeatureCollection")
    
    features = data.get('features', [])
    print(f"\nTotal divisions found: {len(features)}")
    
    if len(features) == EXPECTED_DIVISIONS:
        print(f"[OK] Correct number of divisions ({EXPECTED_DIVISIONS})")
    elif len(features) > 0:
        print(f"[NOTE] Expected {EXPECTED_DIVISIONS} divisions, found {len(features)}")
        print("   (This may be okay if using different year's boundaries)")
    else:
        print("[ERROR] No features found in GeoJSON")
        return False
    
    print()
    
    # Extract and validate division names
    print("Checking division properties...")
    divisions = []
    states = set()
    missing_name = 0
    property_keys = set()
    
    for i, feature in enumerate(features):
        props = feature.get('properties', {})
        property_keys.update(props.keys())
        
        # Try different possible field names for division name
        name = (props.get('Elect_div') or 
                props.get('ELECT_DIV') or
                props.get('name') or 
                props.get('NAME') or
                props.get('Division') or
                props.get('DIVISION') or
                props.get('Divisn_Nm') or
                None)
        
        # Try different possible field names for state
        state = (props.get('State') or 
                 props.get('STATE') or
                 props.get('state') or
                 props.get('State_Ab') or
                 None)
        
        if name:
            divisions.append(name)
            if state:
                states.add(state)
        else:
            missing_name += 1
    
    print(f"   Available properties: {', '.join(sorted(property_keys))}")
    
    if missing_name > 0:
        print(f"[WARNING] {missing_name} divisions missing name field")
        print("   The map will show 'Unknown Division' for these")
    else:
        print("[OK] All divisions have names")
    
    if states:
        print(f"[OK] States found: {', '.join(sorted(states))}")
    
    print()
    
    # Validate coordinates are within Australia
    print("Checking coordinate bounds...")
    coords_outside = 0
    total_coords = 0
    sample_coords = []
    
    for feature in features:
        geom = feature.get('geometry')
        coords = get_nested_coords(geom)
        
        for coord in coords:
            total_coords += 1
            lon, lat = coord[0], coord[1]
            
            # Check if within Australia bounds
            if not (AU_BOUNDS['min_lon'] <= lon <= AU_BOUNDS['max_lon'] and
                    AU_BOUNDS['min_lat'] <= lat <= AU_BOUNDS['max_lat']):
                coords_outside += 1
            
            # Collect sample coords
            if len(sample_coords) < 5:
                sample_coords.append((lon, lat))
    
    print(f"   Total coordinate points: {total_coords:,}")
    
    if coords_outside == 0:
        print("[OK] All coordinates within Australia bounds")
    elif coords_outside < total_coords * 0.01:  # Less than 1%
        print(f"[NOTE] {coords_outside} coordinates outside AU bounds (likely island territories)")
    else:
        print(f"[WARNING] {coords_outside} coordinates outside Australia!")
        print("   This may indicate wrong projection or data issues")
    
    print()
    
    # Show sample divisions
    print("Sample divisions (first 10):")
    for name in sorted(divisions)[:10]:
        print(f"   - {name}")
    if len(divisions) > 10:
        print(f"   ... and {len(divisions) - 10} more")
    
    print()
    
    # Coordinate precision check
    print("Checking coordinate precision...")
    if total_coords > 0:
        sample_coord = sample_coords[0] if sample_coords else (0, 0)
        lon_str = str(sample_coord[0])
        decimals = len(lon_str.split('.')[-1]) if '.' in lon_str else 0
        
        if decimals > 6:
            print(f"[NOTE] High precision ({decimals} decimals) - file could be optimized")
            print("   Tip: 5-6 decimal places is sufficient for electoral boundaries")
        else:
            print(f"[OK] Coordinate precision is reasonable ({decimals} decimals)")
    
    print()
    print("=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    
    # Final recommendation
    if file_size < 5 * 1024 * 1024 and len(features) > 0 and missing_name == 0:
        print("\n[SUCCESS] GeoJSON is ready for use!")
        print("   Toggle electoral boundaries with the vote button on the map.")
    else:
        print("\n[WARNING] GeoJSON may need optimization. See warnings above.")
    
    return True


def show_property_mapping():
    """Show which property names map to what in the Leaflet code"""
    print("\n" + "=" * 60)
    print("PROPERTY NAME MAPPING")
    print("=" * 60)
    print("""
The Leaflet code looks for these property names (in order):

Division Name:
  - Elect_div (AEC standard)
  - name
  - NAME
  - division_name

State:
  - State (AEC standard)
  - state
  - STATE
  - state_name

If your GeoJSON uses different names, you may need to rename them
or update the JavaScript code.
""")


if __name__ == "__main__":
    validate_geojson()
    show_property_mapping()

