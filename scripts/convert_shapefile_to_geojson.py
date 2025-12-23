"""
Convert AEC Electoral Division Shapefile to GeoJSON

This script converts the AEC shapefile to an optimized GeoJSON
suitable for web mapping.

Requirements:
    pip install geopandas

Usage:
    python scripts/convert_shapefile_to_geojson.py "C:\path\to\electoral_divisions.shp"
    
Or place the shapefile in your Downloads folder and run without arguments.
"""

import json
import os
import sys
from pathlib import Path

# Output configuration
SCRIPT_DIR = Path(__file__).parent
OUTPUT_PATH = SCRIPT_DIR.parent / "data" / "electoral-divisions.geojson"

# Coordinate precision (6 decimals ≈ 0.1m precision, plenty for boundaries)
COORD_PRECISION = 5

# Geometry simplification tolerance (in degrees, ~100m at Australian latitudes)
SIMPLIFY_TOLERANCE = 0.001

# Fields to keep in output (set to None to keep all)
FIELDS_TO_KEEP = ['Elect_div', 'State', 'Numccds', 'Actual', 'Area_SqKm']


def find_shapefile():
    """Try to find the shapefile in common locations"""
    common_paths = [
        Path.home() / "Downloads" / "electoral_divisions.shp",
        Path.home() / "Downloads" / "2025-aec-national-esri" / "electoral_divisions.shp",
        Path.home() / "Downloads" / "COM_ELB_region.shp",
        Path.home() / "Downloads" / "COM_ELB.shp",
        SCRIPT_DIR.parent / "data" / "electoral_divisions.shp",
    ]
    
    for path in common_paths:
        if path.exists():
            return path
    
    return None


def round_coords(coords, precision):
    """Recursively round coordinates to specified precision"""
    if isinstance(coords, (list, tuple)):
        if len(coords) >= 2 and all(isinstance(x, (int, float)) for x in coords[:2]):
            # This is a coordinate pair
            return [round(coords[0], precision), round(coords[1], precision)]
        else:
            return [round_coords(c, precision) for c in coords]
    return coords


def optimize_geojson(geojson_dict, precision=COORD_PRECISION, fields=FIELDS_TO_KEEP):
    """Optimize GeoJSON for web use"""
    
    features = geojson_dict.get('features', [])
    optimized_features = []
    
    for feature in features:
        # Reduce coordinate precision
        if feature.get('geometry') and feature['geometry'].get('coordinates'):
            feature['geometry']['coordinates'] = round_coords(
                feature['geometry']['coordinates'], 
                precision
            )
        
        # Keep only specified fields
        if fields and feature.get('properties'):
            old_props = feature['properties']
            new_props = {}
            
            for key in fields:
                # Case-insensitive field matching
                for old_key in old_props:
                    if old_key.lower() == key.lower():
                        new_props[key] = old_props[old_key]
                        break
            
            # Also try to map common variations
            if 'Elect_div' not in new_props:
                for k in ['Divisn_Nm', 'ELECT_DIV', 'Division', 'NAME', 'name']:
                    if k in old_props:
                        new_props['Elect_div'] = old_props[k]
                        break
            
            if 'State' not in new_props:
                for k in ['State_Ab', 'STATE', 'state']:
                    if k in old_props:
                        new_props['State'] = old_props[k]
                        break
            
            feature['properties'] = new_props
        
        optimized_features.append(feature)
    
    geojson_dict['features'] = optimized_features
    return geojson_dict


def convert_shapefile(shapefile_path, output_path, simplify=True):
    """Convert shapefile to optimized GeoJSON"""
    
    try:
        import geopandas as gpd
    except ImportError:
        print("❌ ERROR: geopandas not installed")
        print("\nInstall with:")
        print("    pip install geopandas")
        print("\nOr use the online converter at https://mapshaper.org/")
        return False
    
    shapefile_path = Path(shapefile_path)
    output_path = Path(output_path)
    
    print(f"📂 Reading shapefile: {shapefile_path}")
    
    try:
        gdf = gpd.read_file(shapefile_path)
        print(f"✅ Loaded {len(gdf)} features")
    except Exception as e:
        print(f"❌ ERROR reading shapefile: {e}")
        return False
    
    # Check CRS and reproject if needed
    print(f"📍 Original CRS: {gdf.crs}")
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        print("   Reprojecting to WGS84 (EPSG:4326)...")
        gdf = gdf.to_crs(epsg=4326)
        print("✅ Reprojected to WGS84")
    
    # Simplify geometry
    if simplify:
        original_size = gdf.geometry.apply(lambda g: len(str(g))).sum()
        print(f"🔧 Simplifying geometry (tolerance: {SIMPLIFY_TOLERANCE})...")
        gdf['geometry'] = gdf.geometry.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
        new_size = gdf.geometry.apply(lambda g: len(str(g))).sum()
        reduction = (1 - new_size / original_size) * 100
        print(f"✅ Geometry simplified ({reduction:.1f}% reduction)")
    
    # Show available columns
    print(f"\n📋 Available columns: {list(gdf.columns)}")
    
    # Convert to GeoJSON
    print("\n📝 Converting to GeoJSON...")
    geojson_str = gdf.to_json()
    geojson_dict = json.loads(geojson_str)
    
    # Optimize
    print("🔧 Optimizing for web use...")
    geojson_dict = optimize_geojson(geojson_dict)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_dict, f, separators=(',', ':'))  # Compact JSON
    
    file_size = output_path.stat().st_size
    print(f"\n✅ Saved to: {output_path}")
    print(f"📊 File size: {file_size / 1024 / 1024:.2f} MB")
    
    # Show sample
    if geojson_dict.get('features'):
        sample = geojson_dict['features'][0].get('properties', {})
        print(f"\n📋 Sample division properties:")
        for k, v in sample.items():
            print(f"   {k}: {v}")
    
    return True


def main():
    print("=" * 60)
    print("Shapefile to GeoJSON Converter")
    print("=" * 60)
    print()
    
    # Get shapefile path
    if len(sys.argv) > 1:
        shapefile_path = Path(sys.argv[1])
    else:
        shapefile_path = find_shapefile()
        
        if shapefile_path:
            print(f"Found shapefile at: {shapefile_path}")
        else:
            print("❌ Could not find shapefile automatically.")
            print("\nUsage:")
            print('    python scripts/convert_shapefile_to_geojson.py "C:\\path\\to\\electoral_divisions.shp"')
            print("\nOr place the shapefile in your Downloads folder as 'electoral_divisions.shp'")
            return
    
    if not shapefile_path.exists():
        print(f"❌ File not found: {shapefile_path}")
        return
    
    # Check for companion files
    required_files = ['.shx', '.dbf']
    for ext in required_files:
        companion = shapefile_path.with_suffix(ext)
        if not companion.exists():
            print(f"⚠️  Warning: Missing {companion.name} (may cause issues)")
    
    print()
    
    # Convert
    success = convert_shapefile(shapefile_path, OUTPUT_PATH)
    
    if success:
        print("\n" + "=" * 60)
        print("CONVERSION COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run validation: python scripts/validate_electoral_geojson.py")
        print("2. Test on map: Click the 🗳️ button to toggle boundaries")
    else:
        print("\n" + "=" * 60)
        print("CONVERSION FAILED")
        print("=" * 60)
        print("\nTry the online converter instead:")
        print("1. Go to https://mapshaper.org/")
        print("2. Drag all .shp, .shx, .dbf, .prj files onto the page")
        print("3. Click Export > GeoJSON")


if __name__ == "__main__":
    main()






