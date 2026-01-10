"""
Historical LGBTIQ+ Hate Crime Scraper (2000-2025)
Target: 500-800 incidents
Backfill project for Incidex.
"""

import os
import sys
import logging
import json
import time
import re
import csv
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Import specific modules
from scripts.gemini_extractor import (
    validate_location, 
    validate_date, 
    analyze_incident_detailed, 
    extract_incident
)
from geocoder import Geocoder
from deduplicator import Deduplicator
try:
    from config import RATE_LIMIT_DELAY
except ImportError:
    RATE_LIMIT_DELAY = 1

# Setup Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Check for debug mode from environment variable to set initial log level
initial_log_level = logging.DEBUG if os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes") else logging.INFO

logging.basicConfig(
    level=initial_log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f"historical_scraper_2000_2025_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "incidents_historical_2000_2025.csv"
REVIEW_FILE = DATA_DIR / "review" / "incidents_low_confidence_2000_2025.csv"
DEDUP_REPORT = DATA_DIR / "audit" / "deduplication_report_2000_2025.csv"
PROGRESS_FILE = DATA_DIR / "historical_scraper_progress.json"

# Ensure directories exist
(DATA_DIR / "review").mkdir(exist_ok=True)
(DATA_DIR / "audit").mkdir(exist_ok=True)

class HistoricalScraper2000_2025:
    def __init__(self, dry_run: bool = False, debug_mode: bool = False):
        self.dry_run = dry_run
        self.debug_mode = debug_mode or os.getenv("DEBUG_MODE", "").lower() in ("true", "1", "yes")
        self.geocoder = Geocoder(cache_file=str(BASE_DIR / "geocoding_cache.json"))
        # Using existing Deduplicator but will add custom logic for this specific run
        self.deduplicator = Deduplicator(existing_csv_path=str(DATA_DIR / "incidents_in_progress.csv"))
        
        self.stats = {
            "fetched": 0,
            "stage1_source_rej": 0,
            "stage2_geo_rej": 0,
            "stage3_date_rej": 0,
            "stage4_class_rej": 0,
            "stage5_low_conf": 0,
            "stage6_dupe": 0,
            "accepted": 0
        }
        
        self.incidents_to_save = []
        self.incidents_for_review = []
        self.dedup_log = []
        
        if self.debug_mode:
            logger.info("DEBUG MODE ENABLED - Enhanced logging and relaxed validation thresholds")

    def load_progress(self):
        # Implement resume logic if needed
        pass

    def run_pipeline(self, articles: List[Dict[str, Any]]):
        """
        Main pipeline execution.
        """
        logger.info(f"Starting pipeline with {len(articles)} candidate articles...")
        
        for article in articles:
            self.stats["fetched"] += 1
            title = article.get("title", "")
            text = article.get("text", "") or article.get("snippet", "")
            url = article.get("url", "")
            source = article.get("source", "")
            
            logger.info(f"Processing: {title[:50]}...")

            # STAGE 1: Source Validation
            if not self._validate_source(source, url):
                self.stats["stage1_source_rej"] += 1
                logger.info("  -> Rejected: Invalid Source")
                continue

            # STAGE 2: Geographic Validation
            # Combine title + partial text for cost efficiency
            content_sample = f"{title}\n{text[:1500]}"
            
            # Direct debug print statements for validation
            print("\n=== VALIDATION DEBUG ===")
            print(f"Article: {url}")
            print(f"Text: {content_sample[:500]}")
            
            # Call validate_location with debug=True to get detailed info
            location_result = validate_location(content_sample, debug=True)
            debug_info = None
            
            if isinstance(location_result, tuple):
                is_valid, debug_info = location_result
                
                # Check if there was an API error
                if 'error' in debug_info:
                    print(f"Prompt: [ERROR - API call failed]")
                    print(f"Response: [ERROR - {debug_info.get('error_type', 'Unknown')}]")
                    print(f"Locations: N/A (error occurred)")
                    print(f"Result: FAIL - {debug_info.get('error', 'N/A')}")
                else:
                    prompt_text = debug_info.get('prompt', 'N/A')
                    response_text = debug_info.get('response_text', 'N/A')
                    detected_locations = debug_info.get('detected_location', 'None detected')
                    
                    print(f"Prompt: {prompt_text}")
                    print(f"Response: {response_text}")
                    print(f"Locations: {detected_locations}")
                    print(f"Result: {'PASS' if is_valid else 'FAIL'}")
            else:
                is_valid = location_result
                print(f"Prompt: [Debug info not available]")
                print(f"Response: [Debug info not available]")
                print(f"Locations: [Debug info not available]")
                print(f"Result: {'PASS' if is_valid else 'FAIL'}")
            
            print("======================\n")
            
            if not is_valid:
                rejection_reason = "Non-Australian Location"
                if debug_info:
                    # Use already-retrieved debug info for rejection reason
                    if 'error' in debug_info:
                        rejection_reason = f"API Error: {debug_info.get('error_type', 'Unknown')}"
                    elif 'detected_location' in debug_info:
                        if debug_info.get('detected_location') == 'None detected':
                            rejection_reason = "No Australian location detected in text"
                        else:
                            rejection_reason = f"Location mismatch: {debug_info.get('response_text', 'Unknown reason')}"
                
                self.stats["stage2_geo_rej"] += 1
                logger.info(f"  -> Rejected: {rejection_reason}")
                continue
            
            logger.info("  -> Geographic validation passed")

            # STAGE 3: Date Validation
            if not validate_date(content_sample, 2000, 2025):
                self.stats["stage3_date_rej"] += 1
                logger.info("  -> Rejected: Date out of range")
                continue

            # STAGE 4 & 5: Classification & Confidence
            # This is the 'expensive' call, so we do it last
            analysis = analyze_incident_detailed(title, text)
            
            if not analysis.get("is_hate_crime"):
                self.stats["stage4_class_rej"] += 1
                logger.info("  -> Rejected: Not an LGBTIQ+ hate crime")
                continue
                
            confidence = analysis.get("confidence_score", 0)
            if confidence < 50: # Hard reject very low confidence
                self.stats["stage4_class_rej"] += 1 
                logger.info(f"  -> Rejected: Low confidence ({confidence})")
                continue

            # Prepare Incident Object
            incident = {
                "incident_id": f"hist_{datetime.now().strftime('%Y')}_{self.stats['accepted'] + self.stats['stage5_low_conf'] + 1000}", # Temp ID
                "title": title,
                "description": analysis.get("reasoning", ""), # Initial description from reasoning
                "incident_type": analysis.get("incident_type"),
                "victim_identity": analysis.get("victim_identity"),
                "confidence_score": confidence,
                "article_url": url,
                "news_source": source,
                "verification_status": "high_confidence" if confidence >= 70 else "low_confidence",
                # Extraction of specific fields
                "date_of_incident": "", 
                "location": "",
                "suburb": "",
                "state": "",
                "postcode": "",
                "latitude": "",
                "longitude": ""
            }

            # If High Confidence, do full extraction to get details
            if confidence >= 70:
                extracted_data = extract_incident(title, text, url)
                if extracted_data:
                    incident.update(extracted_data)
                    # Helper to parse location if Gemini didn't return structured separate fields (it usually returns 'location' string)
                    # We will use geocoder on incident['location']
            
            # Geocoding
            if incident.get("location"):
                geo_result = self.geocoder.geocode(incident["location"])
                if geo_result:
                    incident["latitude"] = geo_result.latitude
                    incident["longitude"] = geo_result.longitude
                    incident["suburb"] = geo_result.suburb
                    incident["postcode"] = geo_result.postcode
                    incident["state"] = geo_result.state
            
            # STAGE 6: Deduplication
            if self._is_duplicate(incident):
                self.stats["stage6_dupe"] += 1
                logger.info("  -> Rejected: Duplicate")
                continue

            # Check confidence for final bucket
            if confidence >= 70:
                self.incidents_to_save.append(incident)
                self.stats["accepted"] += 1
                logger.info("  -> Accepted: High Confidence")
            else:
                self.incidents_for_review.append(incident)
                self.stats["stage5_low_conf"] += 1
                logger.info("  -> Flagged for Review: Medium/Low Confidence")
                
            time.sleep(RATE_LIMIT_DELAY) # Rate limiting

        self._save_results()
        self._generate_report()

    def _validate_source(self, source: str, url: str) -> bool:
        """
        Stage 1: Source whitelist/blacklist
        """
        # Basic blacklist
        blacklist = ["opinion", "blog", "reddit.com", "facebook.com", "twitter.com"]
        if any(x in url.lower() for x in blacklist):
            return False
            
        # Trusted sources (Accept list - just heuristics, we default to True for news sites)
        trusted = ["abc.net.au", "sbs.com.au", "theguardian.com", "smh.com.au", "theage.com.au", "news.com.au"]
        
        # If it's a known reliable source, definitely yes.
        # If it's unknown, we heavily rely on the content analysis, so we let it pass Stage 1 unless blacklisted
        return True

    def _is_duplicate(self, incident: Dict) -> bool:
        """
        Stage 6: Deduplication against existing data
        """
        # Create a simplified object for the deduplicator
        # The deduplicator expects a list of dicts. We can use it to check against loaded data.
        # Using a direct fuzzy match here for simplicity or calling the deduplicator class methods.
        
        # We need to check against:
        # 1. Existing progress (self.deduplicator.existing_incidents contains incidents_in_progress.csv)
        # 2. Typically we also check against what we've already found in this run (self.incidents_to_save)
        
        # Combine lists to check against
        existing = self.deduplicator.existing_incidents + self.incidents_to_save
        
        # Use Deduplicator's helper to find match
        # We need to adapt the logic because 'find_duplicates' works on a batch.
        # Let's check manually using the key fields: date, location, type
        
        inc_date = incident.get("date_of_incident")
        inc_loc = incident.get("location")
        inc_type = incident.get("incident_type")
        
        if not inc_date or not inc_loc:
            return False # Can't dedupe without data, let it pass (or fail validation elsewhere)

        for exist in existing:
            # Simple fuzzy check (can be improved with Deduplicator logic if exposed)
            # Date match (exact or close) + Location match (fuzzy)
            exist_date = exist.get("date_of_incident") or exist.get("date")
            exist_loc = exist.get("location")
            
            if not exist_date or not exist_loc:
                continue
                
            # Date Check (Exact string match for now, or use datetime)
            if inc_date == exist_date:
                # Location fuzzy check using deduplicator's method
                if self.deduplicator._locations_match(inc_loc, exist_loc, threshold=80):
                    # Log it
                    self.dedup_log.append({
                        "new_id": incident["incident_id"],
                        "match_id": exist.get("incident_id") or exist.get("id"),
                        "confidence": "High",
                        "reason": "Date and Location Match"
                    })
                    return True
                    
        return False

    def _save_results(self):
        # Save High Confidence
        if self.incidents_to_save:
            keys = self.incidents_to_save[0].keys()
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.incidents_to_save)
            logger.info(f"Saved {len(self.incidents_to_save)} incidents to {OUTPUT_FILE}")

        # Save Review
        if self.incidents_for_review:
            keys = self.incidents_for_review[0].keys()
            with open(REVIEW_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.incidents_for_review)
            logger.info(f"Saved {len(self.incidents_for_review)} incidents to review in {REVIEW_FILE}")
            
        # Save Dedup Log
        if self.dedup_log:
            keys = self.dedup_log[0].keys()
            with open(DEDUP_REPORT, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.dedup_log)

    def _generate_report(self):
        report = f"""# Scraper Report 2000-2025
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Total Fetched**: {self.stats['fetched']}

## Filtering Stats
- Source Rejected: {self.stats['stage1_source_rej']}
- Geography Rejected: {self.stats['stage2_geo_rej']}
- Date Rejected: {self.stats['stage3_date_rej']}
- Not Hate Crime: {self.stats['stage4_class_rej']}
- Low Confidence: {self.stats['stage5_low_conf']}
- Duplicates: {self.stats['stage6_dupe']}

## Success
- **Accepted Incidents**: {self.stats['accepted']}
"""
        with open(DATA_DIR.parent / "SCRAPER_REPORT_2000_2025.md", "w") as f:
            f.write(report)


    def fetch_articles(self, search_terms: List[str], start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """
        Executes search across GDELT (2017+) and Trove (All) for the date range.
        """
        articles = []
        import requests
        
        # Trove integration
        from scripts.historical_archive_access import TroveArchive
        trove = TroveArchive() 
        
        for year in range(start_year, end_year + 1):
            logger.info(f"Searching year {year}...")
            for term in search_terms:
                try:
                    # GDELT Search (Only available from 2017 onwards for DOCS API v2)
                    if year >= 2017:
                        gdelt_results = self._search_gdelt(term, year)
                        articles.extend(gdelt_results)
                    
                    # Trove Search (All years, especially critical for 2000-2016)
                    trove_results = trove.search(term, year, year)
                    articles.extend(trove_results)
                    
                    time.sleep(RATE_LIMIT_DELAY)
                except Exception as e:
                    logger.error(f"Error searching {term} in {year}: {e}")
                    
        logger.info(f"Total articles found after search: {len(articles)}")
        # Remove simple duplicates by URL before pipeline
        unique_articles = {a['url']: a for a in articles}.values()
        return list(unique_articles)

    def _search_gdelt(self, query: str, year: int) -> List[Dict[str, Any]]:
        """
        Search GDELT API for a specific year and query.
        """
        articles_list = []
        GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
        
        start_date = f"{year}0101000000"
        end_date = f"{year}1231235959"
        
        full_query = query if "Australia" in query else f"{query} Australia"
        
        params = {
            "query": full_query,
            "mode": "artlist",
            "maxrecords": 150, 
            "format": "json",
            "sort": "DateDesc",
            "startdatetime": start_date,
            "enddatetime": end_date
        }
        
        try:
            resp = requests.get(GDELT_URL, params=params, timeout=30)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    for art in data.get("articles", []):
                        articles_list.append({
                            "title": art.get("title"),
                            "url": art.get("url"),
                            "source": art.get("domain"),
                            "date": art.get("seendate"), 
                            "text": art.get("snippet", "")
                        })
                except Exception as json_err:
                    logger.warning(f"Failed to parse GDELT JSON for {query} ({year}): {json_err}")
                    logger.debug(f"Response start: {resp.text[:200]}")
            else:
                logger.warning(f"GDELT returned status {resp.status_code} for {query} ({year})")
        except Exception as e:
            logger.warning(f"GDELT request failed for {query} ({year}): {e}")
            
        return articles_list

    def _check_historical_linking(self, incident: Dict):
        """
        STAGE 7: Historical Linking.
        Check if this is an update to an existing historical incident.
        """
        # Logic: Check if the description mentions "sentencing", "conviction", "appeal", "anniversary"
        # AND shares keywords with an existing 20-40 year old case.
        
        desc = incident.get("description", "").lower()
        title = incident.get("title", "").lower()
        
        keywords = ["sentenced", "convicted", "jailed", "guilty", "appeal", "charged", "cold case"]
        if any(w in desc or w in title for w in keywords):
            # Potential update.
            # We assume 'self.deduplicator.existing_incidents' has the historical data.
            # We look for a match in victim name or very specific location + old date.
            pass # Placeholder for advanced logic.
            # For now, we will flag it in 'notes' if it looks like a legal update
            if "19" in desc or "19" in title: # e.g. "1988 meaning"
                 incident["notes"] = (incident.get("notes") or "") + " [POTENTIAL HISTORICAL LINK/UPDATE]"


def test_single_article(scraper: HistoricalScraper2000_2025, test_article: Dict[str, Any]):
    """
    Test function to run a single article through the validation pipeline.
    """
    logger.info("=" * 80)
    logger.info("TEST MODE: Processing single article through validation pipeline")
    logger.info("=" * 80)
    
    articles = [test_article]
    scraper.run_pipeline(articles)
    
    logger.info("=" * 80)
    logger.info("TEST COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Historical LGBTIQ+ Hate Crime Scraper (2000-2025)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with enhanced logging')
    parser.add_argument('--test', action='store_true', help='Test mode: process a single test article')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode: do not save results')
    args = parser.parse_args()
    
    # Update log level if debug mode is enabled via command line
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.info("Debug logging enabled via --debug flag")
    
    # Initialize scraper with debug mode
    scraper = HistoricalScraper2000_2025(dry_run=args.dry_run, debug_mode=args.debug)
    
    # Test mode: process a single test article
    if args.test:
        logger.info("TEST MODE: Processing single test article")
        
        # Create a test article - replace with actual test data
        test_article = {
            "title": "LGBTIQ community member attacked in Sydney CBD",
            "text": """
            A member of the LGBTIQ community was violently attacked in Sydney's Central Business District 
            on Saturday evening. The incident occurred around 9pm near Hyde Park, where a 28-year-old man 
            was subjected to homophobic slurs before being physically assaulted. 
            
            Police have confirmed they are treating this as a hate crime. The victim, who wishes to remain 
            anonymous, was walking with friends when a group of individuals approached them shouting 
            anti-gay slurs. The attack resulted in minor injuries requiring medical treatment.
            
            NSW Police are investigating and have appealed for witnesses. This incident comes amid rising 
            concerns about LGBTIQ+ safety in Australian cities.
            """,
            "url": "https://example.com/test-article-sydney",
            "source": "example.com",
            "date": "2024-01-15"
        }
        
        test_single_article(scraper, test_article)
        logger.info("Script Complete (Test Mode).")
        sys.exit(0)
    
    # SEARCH STRATEGY - EXPANDED & HISTORICALLY APPROPRIATE
    # ---------------------------------------------------------
    # Broader terms to capture more incidents, including historical terminology
    search_terms = [
        "LGBTIQ hate crime",
        "assault transgender Australia",
        "gay bash Australia",
        "lesbian attack",
        "homophobic violence Australia",
        "transphobic attack",
        "anti-gay assault",
        "queer bash",
        "LGBTIQ discrimination violence",
        "hate speech LGBTIQ Australia",
        "bash gay Sydney",
        "attack transgender Melbourne",
        "violence Brisbane LGBTIQ",
        "hate crime Perth gay",
        "assault Adelaide transgender",
        # Historical terms (2000-2010 focus)
        "homosexual assault Australia",
        "homosexual violence",
        "attack on homosexual",
        "gay murder Australia",
        "transgender violence",
        "transvestite assault", # Historical term
        "sodomy law protest" # Sometimes leads to reports of harassment
    ]
    
    logger.info("Executing expanded Search Strategy (2000-2025)...")
    if args.debug:
        logger.info("Debug mode enabled - will show detailed validation information")
    
    try:
        # Full historical search
        fetched_articles = scraper.fetch_articles(search_terms, 2000, 2025)
        
        # Pipeline execution with rate limiting safety
        if fetched_articles:
            scraper.run_pipeline(fetched_articles)
        else:
            logger.warning("No articles found with the expanded search strategy.")
            
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())

    logger.info("Script Complete.")

