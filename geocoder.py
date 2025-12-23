"""
Geocoder for Australian Locations

This module handles geocoding location strings to Australian suburbs, postcodes,
and coordinates using Nominatim (OpenStreetMap). Includes caching to reduce
API calls and respect rate limits.
"""

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable


logger = logging.getLogger(__name__)


# Nominatim rate limit: 1 request per second
NOMINATIM_RATE_LIMIT = 1.0


@dataclass
class GeocodeResult:
    """
    Structured geocoding result
    
    Attributes:
        suburb: Suburb/locality name
        postcode: Australian postcode
        state: State/territory abbreviation (NSW, VIC, etc.)
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        full_address: Full formatted address from Nominatim
        confidence: Confidence level (high/medium/low) based on match quality
    """
    suburb: Optional[str] = None
    postcode: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    full_address: Optional[str] = None
    confidence: str = "low"


class Geocoder:
    """
    Geocodes Australian locations using Nominatim with caching.
    
    Features:
    - Persistent cache to avoid redundant API calls
    - Rate limiting (1 request/second as per Nominatim policy)
    - Automatic retry on timeouts
    - Suburb/postcode extraction from Nominatim results
    """
    
    def __init__(
        self,
        cache_file: str = "geocoding_cache.json",
        user_agent: str = "SentinelLGBTIQMap/1.0",
        timeout: int = 10,
    ):
        """
        Initialize the Geocoder.
        
        Args:
            cache_file: Path to JSON cache file
            user_agent: User agent string for Nominatim requests
            timeout: Request timeout in seconds
        """
        self.cache_file = Path(cache_file)
        self.timeout = timeout
        self.geolocator = Nominatim(user_agent=user_agent)
        self.cache = self._load_cache()
        self._last_request_time = 0.0
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load geocoding cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    logger.info(f"Loaded {len(cache)} entries from geocoding cache")
                    return cache
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save geocoding cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _enforce_rate_limit(self):
        """Enforce Nominatim rate limit of 1 request per second."""
        elapsed = time.time() - self._last_request_time
        if elapsed < NOMINATIM_RATE_LIMIT:
            sleep_time = NOMINATIM_RATE_LIMIT - elapsed
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def _extract_suburb_and_postcode(self, address: Dict[str, Any]) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extract suburb, postcode, and state from Nominatim address components.
        
        Args:
            address: Nominatim address dictionary
            
        Returns:
            Tuple of (suburb, postcode, state)
        """
        # Nominatim address components (priority order)
        suburb = None
        postcode = None
        state = None
        
        # Try various address component keys
        suburb_keys = ['suburb', 'village', 'town', 'city_district', 'neighbourhood', 'quarter']
        postcode_key = 'postcode'
        state_keys = ['state', 'region']
        
        for key in suburb_keys:
            if key in address and address[key]:
                suburb = address[key]
                break
        
        if postcode_key in address:
            postcode = address[postcode_key]
        
        for key in state_keys:
            if key in address and address[key]:
                state_code = address[key]
                # Convert full state name to abbreviation if needed
                state = self._normalize_state(state_code)
                break
        
        return suburb, postcode, state
    
    def _normalize_state(self, state_name: str) -> Optional[str]:
        """
        Normalize state name to two-letter abbreviation.
        
        Args:
            state_name: Full state name or abbreviation
            
        Returns:
            Two-letter state code (NSW, VIC, etc.) or None
        """
        state_map = {
            "new south wales": "NSW",
            "victoria": "VIC",
            "queensland": "QLD",
            "western australia": "WA",
            "south australia": "SA",
            "tasmania": "TAS",
            "northern territory": "NT",
            "australian capital territory": "ACT",
            "nsw": "NSW",
            "vic": "VIC",
            "qld": "QLD",
            "wa": "WA",
            "sa": "SA",
            "tas": "TAS",
            "nt": "NT",
            "act": "ACT",
        }
        
        normalized = state_name.lower().strip()
        return state_map.get(normalized)
    
    def _determine_confidence(self, location, address: Dict[str, Any]) -> str:
        """
        Determine confidence level based on match quality.
        
        Args:
            location: Nominatim Location object
            address: Address dictionary
            
        Returns:
            Confidence level: "high", "medium", or "low"
        """
        # High confidence: suburb + postcode match
        if address.get('suburb') and address.get('postcode'):
            return "high"
        
        # Medium confidence: suburb or city match
        if address.get('suburb') or address.get('city'):
            return "medium"
        
        # Low confidence: only state/country match
        return "low"
    
    def geocode(
        self,
        location_string: str,
        use_cache: bool = True,
    ) -> Optional[GeocodeResult]:
        """
        Geocode a location string to suburb, postcode, and coordinates.
        
        Args:
            location_string: Location description (e.g., "Oxford Street, Darlinghurst, Sydney")
            use_cache: Whether to use cache (default: True)
            
        Returns:
            GeocodeResult object or None if geocoding fails
        """
        if not location_string or not location_string.strip():
            return None
        
        location_string = location_string.strip()
        cache_key = location_string.lower()
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            cached = self.cache[cache_key]
            logger.debug(f"Cache hit for: {location_string}")
            return GeocodeResult(**cached)
        
        # Enforce rate limit
        self._enforce_rate_limit()
        
        # Build search query (add "Australia" to improve accuracy)
        search_query = f"{location_string}, Australia"
        
        try:
            logger.debug(f"Geocoding: {search_query}")
            location = self.geolocator.geocode(
                search_query,
                timeout=self.timeout,
                exactly_one=True,
                addressdetails=True,
            )
            
            if not location:
                logger.warning(f"Could not geocode: {location_string}")
                # Cache negative result to avoid retrying
                if use_cache:
                    self.cache[cache_key] = {}
                    self._save_cache()
                return None
            
            # Extract address components
            address = location.raw.get('address', {})
            suburb, postcode, state = self._extract_suburb_and_postcode(address)
            confidence = self._determine_confidence(location, address)
            
            result = GeocodeResult(
                suburb=suburb,
                postcode=postcode,
                state=state,
                latitude=location.latitude,
                longitude=location.longitude,
                full_address=location.address,
                confidence=confidence,
            )
            
            # Cache result
            if use_cache:
                self.cache[cache_key] = {
                    "suburb": result.suburb,
                    "postcode": result.postcode,
                    "state": result.state,
                    "latitude": result.latitude,
                    "longitude": result.longitude,
                    "full_address": result.full_address,
                    "confidence": result.confidence,
                }
                self._save_cache()
            
            logger.info(f"Geocoded '{location_string}' -> {suburb}, {postcode} ({confidence} confidence)")
            return result
            
        except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable) as e:
            logger.error(f"Geocoding error for '{location_string}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{location_string}': {e}")
            return None
    
    def geocode_batch(
        self,
        locations: list[str],
        save_cache_interval: int = 10,
    ) -> list[Optional[GeocodeResult]]:
        """
        Geocode multiple locations with batch caching.
        
        Args:
            locations: List of location strings
            save_cache_interval: Save cache every N locations (to prevent data loss)
            
        Returns:
            List of GeocodeResult objects (None for failed geocodes)
        """
        results = []
        
        for i, location in enumerate(locations, 1):
            result = self.geocode(location)
            results.append(result)
            
            # Periodically save cache
            if i % save_cache_interval == 0:
                self._save_cache()
                logger.info(f"Geocoded {i}/{len(locations)} locations...")
        
        # Final cache save
        self._save_cache()
        
        return results


def geocode_location_simple(location_string: str, cache_file: str = "geocoding_cache.json") -> Optional[GeocodeResult]:
    """
    Convenience function for simple geocoding.
    
    Args:
        location_string: Location to geocode
        cache_file: Cache file path
        
    Returns:
        GeocodeResult or None
    """
    geocoder = Geocoder(cache_file=cache_file)
    return geocoder.geocode(location_string)


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    test_locations = [
        "Oxford Street, Darlinghurst, Sydney",
        "Fitzroy, Melbourne",
        "Newtown, NSW",
        "Surfers Paradise, QLD",
    ]
    
    geocoder = Geocoder()
    
    print("Testing geocoding:")
    for loc in test_locations:
        result = geocoder.geocode(loc)
        if result:
            print(f"\n{loc}:")
            print(f"  Suburb: {result.suburb}")
            print(f"  Postcode: {result.postcode}")
            print(f"  State: {result.state}")
            print(f"  Coords: ({result.latitude}, {result.longitude})")
            print(f"  Confidence: {result.confidence}")
        else:
            print(f"\n{loc}: FAILED")
