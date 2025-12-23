"""
Extract and organize state electoral division GeoJSON files from ZIP archives

This script:
1. Finds ZIP files in Downloads folder
2. Extracts GeoJSON files (or converts shapefiles to GeoJSON)
3. Validates them
4. Copies to /data/state-electoral-divisions/ with standardized names
"""

import os
import zipfile
import json
import shutil
from pathlib import Path

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("WARNING: geopandas not installed. Shapefile conversion will not be available.")
    print("Install with: pip install geopandas")

DOWNLOADS_PATH = Path.home() / "Downloads"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "state-electoral-divisions"

# Mapping of ZIP file patterns to state codes and output filenames
STATE_MAPPING = {
    "nsw": {"pattern": "NSW", "output": "nsw.geojson", "name": "New South Wales"},
    "vic": {"pattern": "Vic", "output": "vic.geojson", "name": "Victoria"},
    "qld": {"pattern": "qld", "output": "qld.geojson", "name": "Queensland"},
    "wa": {"pattern": "WA", "output": "wa.geojson", "name": "Western Australia"},
    "sa": {"pattern": "sa", "output": "sa.geojson", "name": "South Australia"},
    "tas": {"pattern": "tas", "output": "tas.geojson", "name": "Tasmania"},
    "act": {"pattern": "ACT", "output": "act.geojson", "name": "Australian Capital Territory"},
    "nt": {"pattern": "NT", "output": "nt.geojson", "name": "Northern Territory"},
}

def find_zip_files():
    """Find relevant ZIP files in Downloads"""
    zip_files = {}
    
    for zip_path in DOWNLOADS_PATH.glob("*.zip"):
        zip_name_lower = zip_path.name.lower()
        
        for state_code, info in STATE_MAPPING.items():
            if info["pattern"].lower() in zip_name_lower and "esri" in zip_name_lower:
                # Prefer files without "(1)" suffix (duplicates)
                if state_code not in zip_files or "(1)" not in zip_path.name:
                    zip_files[state_code] = zip_path
                elif "(1)" not in zip_files[state_code].name:
                    # Keep the one without (1)
                    pass
                else:
                    zip_files[state_code] = zip_path
                break
    
    return zip_files

def extract_geojson_from_zip(zip_path, state_code):
    """Extract GeoJSON file from ZIP archive"""
    print(f"\nExtracting {state_code.upper()} from {zip_path.name}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all files in ZIP
            file_list = zip_ref.namelist()
            
            # Find GeoJSON file
            geojson_file = None
            for file_name in file_list:
                if file_name.endswith('.geojson'):
                    geojson_file = file_name
                    break
            
            if not geojson_file:
                # Check for shapefile that might need conversion
                shp_files = [f for f in file_list if f.endswith('.shp')]
                if shp_files and HAS_GEOPANDAS:
                    print(f"  Found shapefile, converting to GeoJSON: {shp_files[0]}")
                    # Extract entire shapefile (all related files)
                    temp_dir = OUTPUT_DIR / "temp"
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Extract all shapefile components
                    for file_name in file_list:
                        if any(file_name.startswith(shp_files[0].replace('.shp', '')) for _ in [1]):
                            zip_ref.extract(file_name, temp_dir)
                        elif file_name.startswith(os.path.dirname(shp_files[0]) or ''):
                            zip_ref.extract(file_name, temp_dir)
                    
                    # Find the .shp file path
                    shp_path = temp_dir / shp_files[0]
                    if not shp_path.exists():
                        # Try without directory structure
                        shp_name = os.path.basename(shp_files[0])
                        shp_path = temp_dir / shp_name
                    
                    if shp_path.exists():
                        try:
                            # Convert shapefile to GeoJSON
                            gdf = gpd.read_file(str(shp_path))
                            geojson_path = temp_dir / f"{state_code}_converted.geojson"
                            gdf.to_file(str(geojson_path), driver='GeoJSON')
                            return geojson_path
                        except Exception as e:
                            print(f"  ERROR: Failed to convert shapefile: {e}")
                            return None
                    else:
                        print(f"  ERROR: Shapefile not found after extraction")
                        return None
                elif shp_files:
                    print(f"  WARNING: Found shapefile but geopandas not available.")
                    print(f"     Install geopandas to enable automatic conversion.")
                    return None
                return None
            
            # Extract to temp location
            temp_dir = OUTPUT_DIR / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            zip_ref.extract(geojson_file, temp_dir)
            extracted_path = temp_dir / geojson_file
            
            return extracted_path
            
    except Exception as e:
        print(f"  ERROR: Error extracting {zip_path.name}: {e}")
        return None

def validate_geojson(file_path):
    """Validate GeoJSON file structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check basic structure
        if data.get('type') not in ['FeatureCollection', 'Feature']:
            return False, "Invalid GeoJSON type"
        
        # Check for features
        if data.get('type') == 'FeatureCollection':
            features = data.get('features', [])
            if len(features) == 0:
                return False, "No features found"
        
        # Check file size (reasonable limit)
        file_size = file_path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB
            return False, f"File too large: {file_size / 1024 / 1024:.1f}MB"
        
        return True, f"Valid GeoJSON with {len(features) if 'features' in data else 1} feature(s)"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("=" * 60)
    print("State Electoral Division GeoJSON Extractor")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find ZIP files
    zip_files = find_zip_files()
    
    print(f"\nFound {len(zip_files)} state ZIP files:")
    for state_code, zip_path in zip_files.items():
        print(f"  {state_code.upper()}: {zip_path.name}")
    
    # Extract and process each
    results = {}
    
    for state_code, zip_path in zip_files.items():
        state_info = STATE_MAPPING[state_code]
        output_path = OUTPUT_DIR / state_info["output"]
        
        # Extract GeoJSON
        extracted = extract_geojson_from_zip(zip_path, state_code)
        
        if not extracted:
            print(f"  ERROR: Failed to extract {state_code.upper()}")
            results[state_code] = {"status": "failed", "reason": "No GeoJSON found in ZIP"}
            continue
        
        # Validate
        is_valid, message = validate_geojson(extracted)
        
        if not is_valid:
            print(f"  ERROR: Validation failed: {message}")
            results[state_code] = {"status": "failed", "reason": message}
            extracted.unlink()  # Clean up
            continue
        
        # Copy to final location
        shutil.copy2(extracted, output_path)
        extracted.unlink()  # Clean up temp file
        
        # Get file size
        file_size = output_path.stat().st_size / 1024  # KB
        
        print(f"  SUCCESS: Extracted and validated: {state_info['output']} ({file_size:.1f} KB)")
        print(f"     {message}")
        
        results[state_code] = {
            "status": "success",
            "file": str(output_path),
            "size_kb": file_size,
            "message": message
        }
    
    # Clean up temp directory
    temp_dir = OUTPUT_DIR / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    successful = [s for s, r in results.items() if r.get("status") == "success"]
    failed = [s for s, r in results.items() if r.get("status") != "success"]
    
    print(f"\nSUCCESS: Successfully extracted {len(successful)} states")
    for state_code in successful:
        info = STATE_MAPPING[state_code]
        result = results[state_code]
        print(f"   {info['name']}: {info['output']} ({result['size_kb']:.1f} KB)")
    
    if failed:
        print(f"\nFAILED: {len(failed)} states")
        for state_code in failed:
            info = STATE_MAPPING[state_code]
            reason = results[state_code].get("reason", "Unknown error")
            print(f"   {info['name']}: {reason}")
    
    # Check for missing states
    missing = set(STATE_MAPPING.keys()) - set(zip_files.keys())
    if missing:
        print(f"\nWARNING: Missing ZIP files: {', '.join([STATE_MAPPING[s]['name'] for s in missing])}")
        print("   These states will need to be added manually.")
    
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Review extracted GeoJSON files")
    print("2. Generate state MP voting data")
    print("3. Implement state map overlays")

if __name__ == "__main__":
    main()

