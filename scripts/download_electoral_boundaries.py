"""
Download Australian Electoral Commission (AEC) Federal Electoral Division Boundaries

This script downloads the official AEC electoral division GeoJSON and prepares it
for use with the hate crime map overlay.

Data Source: AEC via data.gov.au
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# AEC Electoral Boundaries download URLs
# The AEC publishes boundaries in various formats - we use GeoJSON/Shapefile
AEC_DATA_SOURCES = [
    # Simplified GeoJSON (smaller file size, good for web maps)
    {
        "name": "AEC Electoral Divisions 2024 (Simplified)",
        "url": "https://data.gov.au/data/dataset/aec-electoral-boundaries-for-australia/resource/1d9be57f-3c13-4b60-a58f-e37b3a0fb65f/download",
        "format": "geojson"
    },
    # Alternative: Full resolution boundaries
    {
        "name": "AEC Electoral Divisions 2024 (Full)",
        "url": "https://aec.gov.au/Electorates/gis/files/2024-aec-shp.zip",
        "format": "shapefile"
    }
]

# Output path
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "electoral-divisions.geojson"


def download_geojson(url: str, output_path: Path) -> bool:
    """
    Download GeoJSON file from URL
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Downloading from: {url}")
    print("This may take a moment...")
    
    try:
        # Create request with user agent
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
            
            # Try to parse as JSON to validate
            geojson = json.loads(data)
            
            # Validate structure
            if 'type' not in geojson:
                print("Error: Invalid GeoJSON - missing 'type' field")
                return False
                
            if geojson['type'] == 'FeatureCollection':
                feature_count = len(geojson.get('features', []))
                print(f"✓ Valid GeoJSON with {feature_count} electoral divisions")
            elif geojson['type'] == 'Feature':
                print("✓ Valid GeoJSON (single feature)")
            else:
                print(f"Warning: Unexpected GeoJSON type: {geojson['type']}")
            
            # Save to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson, f)
                
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✓ Saved to: {output_path}")
            print(f"  File size: {file_size:.2f} MB")
            
            return True
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return False
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def simplify_geojson(input_path: Path, output_path: Path, tolerance: float = 0.001) -> bool:
    """
    Simplify GeoJSON geometry to reduce file size (requires shapely)
    
    Args:
        input_path: Path to input GeoJSON
        output_path: Path for simplified output
        tolerance: Simplification tolerance (larger = more simplified)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from shapely.geometry import shape, mapping
        from shapely.ops import transform
        
        print(f"Simplifying geometry (tolerance: {tolerance})...")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            geojson = json.load(f)
            
        simplified_features = []
        
        for feature in geojson.get('features', []):
            if feature.get('geometry'):
                geom = shape(feature['geometry'])
                simplified_geom = geom.simplify(tolerance, preserve_topology=True)
                feature['geometry'] = mapping(simplified_geom)
            simplified_features.append(feature)
            
        geojson['features'] = simplified_features
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f)
            
        original_size = input_path.stat().st_size / (1024 * 1024)
        new_size = output_path.stat().st_size / (1024 * 1024)
        reduction = (1 - new_size / original_size) * 100
        
        print(f"✓ Simplified: {original_size:.2f} MB → {new_size:.2f} MB ({reduction:.1f}% reduction)")
        return True
        
    except ImportError:
        print("Note: Install 'shapely' package for geometry simplification")
        return False
    except Exception as e:
        print(f"Simplification error: {e}")
        return False


def create_sample_geojson(output_path: Path) -> None:
    """
    Create a sample GeoJSON file with a few example divisions
    for testing purposes when download fails
    """
    sample = {
        "type": "FeatureCollection",
        "name": "AEC_Sample_Divisions",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "Elect_div": "Melbourne",
                    "State": "VIC"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [144.92, -37.86], [144.99, -37.86],
                        [144.99, -37.78], [144.92, -37.78],
                        [144.92, -37.86]
                    ]]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "Elect_div": "Sydney",
                    "State": "NSW"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [151.18, -33.92], [151.24, -33.92],
                        [151.24, -33.84], [151.18, -33.84],
                        [151.18, -33.92]
                    ]]
                }
            }
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample, f, indent=2)
    
    print(f"✓ Created sample GeoJSON at: {output_path}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("AEC Electoral Boundaries Downloader")
    print("=" * 60)
    print()
    
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Check if file already exists
    if OUTPUT_FILE.exists():
        response = input(f"File already exists at {OUTPUT_FILE}. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Try each data source
    success = False
    for source in AEC_DATA_SOURCES:
        if source['format'] == 'geojson':
            print(f"\nTrying: {source['name']}")
            if download_geojson(source['url'], OUTPUT_FILE):
                success = True
                break
        else:
            print(f"\nSkipping {source['name']} (format: {source['format']})")
    
    if not success:
        print("\n" + "=" * 60)
        print("DOWNLOAD FAILED")
        print("=" * 60)
        print("""
The automatic download failed. Please manually download the electoral
boundaries from one of these sources:

1. data.gov.au (Recommended):
   https://data.gov.au/dataset/aec-electoral-boundaries-australia
   
2. AEC Website (Shapefiles):
   https://www.aec.gov.au/Electorates/gis/index.htm
   
3. GitHub (Community maintained):
   https://github.com/aaronsnoswell/aus-federal-electoral-boundary-data

After downloading, save the GeoJSON file to:
{output_path}

The GeoJSON should have this structure:
{{
  "type": "FeatureCollection",
  "features": [
    {{
      "type": "Feature",
      "properties": {{
        "Elect_div": "Division Name",
        "State": "STATE"
      }},
      "geometry": {{ ... }}
    }}
  ]
}}
""".format(output_path=OUTPUT_FILE))
        
        # Create sample file for testing
        create_sample = input("\nCreate a sample file for testing? [y/N]: ")
        if create_sample.lower() == 'y':
            create_sample_geojson(OUTPUT_FILE)
    else:
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"""
Electoral boundaries downloaded successfully!

File saved to: {OUTPUT_FILE}

You can now use the electoral divisions overlay on your map.
Click the 🗳️ button in the map controls to toggle the layer.
""")


if __name__ == "__main__":
    main()






