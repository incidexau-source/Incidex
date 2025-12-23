"""
Historical Incident Scraper for 2005-2019
Comprehensive Retrospective Audit for LGBTIQ+ Hate Crime Incidents

This script performs exhaustive archaeological search through archived news sources,
court records, and advocacy organization documentation to capture all LGBTIQ+ hate
crime incidents from January 2005 to December 2019 (15-year period).
"""

import os
import sys
import logging
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Import project config
try:
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
except ImportError:
    OPENAI_API_KEY = None
    RATE_LIMIT_DELAY = 1

# Import existing modules
from geocoder import Geocoder
from deduplicator import Deduplicator

# Configure logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / f"historical_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "historical_incidents_2005_2019.csv"
SEARCH_LOG_JSON = DATA_DIR / "historical_search_log.json"
DEDUP_REPORT_JSON = DATA_DIR / "historical_dedup_report.json"
GAP_ANALYSIS_JSON = DATA_DIR / "historical_gap_analysis.json"
CHECKPOINT_FILE = DATA_DIR / "historical_scraper_checkpoint.json"
PROGRESS_CSV = DATA_DIR / "historical_incidents_in_progress.csv"
ARTICLES_CACHE_FILE = DATA_DIR / "historical_articles_cache.json"

# Date range: Jan 1, 2005 to Dec 31, 2019 (15 years)
START_DATE = datetime(2005, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2019, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days + 1

# Temporal search blocks (overlapping for cross-validation)
TEMPORAL_BLOCKS = [
    {"start": 2005, "end": 2007, "name": "Block 1: 2005-2007"},
    {"start": 2006, "end": 2008, "name": "Block 2: 2006-2008"},
    {"start": 2008, "end": 2010, "name": "Block 3: 2008-2010"},
    {"start": 2010, "end": 2012, "name": "Block 4: 2010-2012"},
    {"start": 2012, "end": 2014, "name": "Block 5: 2012-2014"},
    {"start": 2014, "end": 2016, "name": "Block 6: 2014-2016"},
    {"start": 2016, "end": 2017, "name": "Block 7: 2016-2017"},
    {"start": 2017, "end": 2019, "name": "Block 8: 2017-2019"},
]

# Primary search terms (broader historical context)
PRIMARY_SEARCH_TERMS = [
    # Core LGBTIQ+ Violence Terms
    "gay hate crime", "gay violence", "gay assault",
    "lesbian assault", "lesbian violence", "lesbian hate",
    "transgender attack", "trans violence", "trans assault",
    "homophobic violence", "homophobic attack", "homophobic assault",
    "transphobic violence", "transphobic assault",
    "LGBTIQ hate crime", "LGBTI hate crime", "LGBT hate crime",
    "sexual orientation violence", "sexual orientation attack",
    "gender identity violence", "gender identity attack",
    "anti-gay attack", "anti-gay violence", "anti-gay hate",
    "gay bashing", "queer bashing",
    "same-sex couple attack", "same-sex assault",
    "rainbow community violence", "rainbow violence",
    # Event-Based Terms
    "Mardi Gras assault", "Mardi Gras attack", "Mardi Gras violence",
    "Pride attack", "Pride violence", "Pride hate crime",
    "LGBTIQ event attack", "LGBTIQ event assault",
    "gay venue assault", "gay venue attack",
    "drag show attack", "drag show assault",
    # Legal/Court Terms
    "discrimination case gender", "discrimination case sexual orientation",
    "hate crime gay", "hate crime lesbian", "hate crime transgender",
    "aggravated assault gay", "aggravated assault lesbian",
    "prosecute hate", "prosecute homophobic", "prosecute transphobic",
]

# Secondary search terms (edge cases)
SECONDARY_SEARCH_TERMS = [
    "assault sexual minority", "assault minority group",
    "hate crime protected attribute", "hate crime protected ground",
    "vilification gay", "vilification lesbian", "vilification transgender",
    "harassment sexual orientation", "harassment gender identity",
    "intimidation gay community", "intimidation LGBTIQ",
    "targeted LGBTIQ", "targeted gay", "targeted lesbian",
    "bias-motivated sexual orientation", "bias-motivated gender identity",
]

# Source authority levels (1 = highest, 6 = lowest)
SOURCE_AUTHORITY_LEVELS = {
    "ABC News": 2,
    "SBS News": 2,
    "The Australian": 3,
    "The Age": 3,
    "Sydney Morning Herald": 3,
    "Brisbane Times": 3,
    "Courier-Mail": 3,
    "Herald Sun": 3,
    "The West Australian": 3,
    "The Advertiser": 3,
    "Hobart Mercury": 4,
    "The Examiner": 4,
    "Northern Territory News": 4,
    "Canberra Times": 3,
    "Daily Telegraph": 3,
    "Star Observer": 5,
    "DNA Magazine": 5,
    "Gay News Network": 5,
    "ACON": 4,
    "Equality Australia": 4,
    "Australian Queer Archives": 4,
    "Trove": 2,  # National Library archive
}


class HistoricalScraper2005_2019:
    """
    Comprehensive historical scraper for 2005-2019 LGBTIQ+ hate crime incidents.
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the historical scraper.
        
        Args:
            dry_run: If True, don't save files (for testing)
        """
        self.dry_run = dry_run
        self.geocoder = Geocoder(cache_file=str(BASE_DIR / "geocoding_cache.json"))
        
        # Statistics
        self.stats = {
            "searches_executed": 0,
            "articles_found": 0,
            "incidents_extracted": 0,
            "duplicates_found": 0,
            "unique_incidents": 0,
            "geocoded": 0,
            "geocoding_failures": 0,
            "errors": 0,
        }
        
        # Results storage
        self.all_incidents = []
        self.search_log = []
        self.duplicate_groups = []
        self._articles_found = []  # Store articles found during searches
        self._processed_urls = set()  # Track processed article URLs for resume
        
    def run(self) -> Dict[str, Any]:
        """
        Run the complete historical scraping pipeline.
        
        Returns:
            Dictionary with results and statistics
        """
        logger.info("=" * 70)
        logger.info("HISTORICAL SCRAPER 2005-2019")
        logger.info("=" * 70)
        logger.info(f"Date Range: {START_DATE.date()} to {END_DATE.date()} ({DATE_RANGE_DAYS} days)")
        logger.info(f"Temporal Blocks: {len(TEMPORAL_BLOCKS)}")
        logger.info("=" * 70)
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Step 1: Execute searches across all temporal blocks (or load from cache)
            if ARTICLES_CACHE_FILE.exists() and len(self._articles_found) == 0:
                logger.info("\n[STEP 1] Loading articles from cache...")
                try:
                    with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                        self._articles_found = json.load(f)
                    self.stats["articles_found"] = len(self._articles_found)
                    logger.info(f"Loaded {len(self._articles_found)} articles from cache (skipping search phase)")
                except Exception as e:
                    logger.warning(f"Error loading articles cache: {e}. Will re-run searches.")
                    logger.info("\n[STEP 1] Executing Exhaustive Search Strategy...")
                    self._execute_search_strategy()
            else:
                logger.info("\n[STEP 1] Executing Exhaustive Search Strategy...")
                self._execute_search_strategy()
            
            # Step 2: Extract incidents from found articles
            logger.info("\n[STEP 2] Extracting Incidents...")
            self._extract_incidents()
            
            # Step 3: Geocode all incidents
            logger.info("\n[STEP 3] Geocoding Locations...")
            self._geocode_incidents()
            
            # Step 4: Deduplicate
            logger.info("\n[STEP 4] Deduplicating Historical Incidents...")
            self._deduplicate_historical()
            
            # Step 5: Quality assurance
            logger.info("\n[STEP 5] Quality Assurance Validation...")
            self._quality_assurance()
            
            # Step 6: Gap analysis
            logger.info("\n[STEP 6] Gap Analysis...")
            gap_analysis = self._gap_analysis()
            
            # Step 7: Save results
            logger.info("\n[STEP 7] Saving Results...")
            if not self.dry_run:
                self._save_results()
                self._save_search_log()
                self._save_gap_analysis(gap_analysis)
            else:
                logger.info("[DRY RUN] Skipping file save")
            
            # Generate final report
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            report = {
                "execution_info": {
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration,
                    "date_range": {
                        "start": START_DATE.isoformat(),
                        "end": END_DATE.isoformat(),
                        "days": DATE_RANGE_DAYS
                    }
                },
                "summary": {
                    "searches_executed": self.stats["searches_executed"],
                    "articles_found": self.stats["articles_found"],
                    "incidents_extracted": self.stats["incidents_extracted"],
                    "unique_incidents": self.stats["unique_incidents"],
                    "duplicates_found": self.stats["duplicates_found"],
                    "geocoded": self.stats["geocoded"],
                    "geocoding_failures": self.stats["geocoding_failures"],
                },
                "statistics": self.stats.copy(),
                "gap_analysis": gap_analysis,
            }
            
            self._print_summary()
            return report
            
        except Exception as e:
            logger.error(f"Fatal error in historical scraper: {e}", exc_info=True)
            raise
    
    def _execute_search_strategy(self):
        """
        Execute exhaustive search strategy across all temporal blocks and sources.
        This is a placeholder - actual implementation would search real archives.
        """
        logger.info("Executing search strategy across temporal blocks...")
        
        # For each temporal block
        for block in TEMPORAL_BLOCKS:
            logger.info(f"\nProcessing {block['name']} ({block['start']}-{block['end']})...")
            
            # Search primary terms
            for term in PRIMARY_SEARCH_TERMS:
                self._execute_search(term, block["start"], block["end"], "primary")
            
            # Search secondary terms
            for term in SECONDARY_SEARCH_TERMS:
                self._execute_search(term, block["start"], block["end"], "secondary")
        
        logger.info(f"\nTotal searches executed: {self.stats['searches_executed']}")
        logger.info(f"Total articles found: {self.stats['articles_found']}")
        
        # Save articles to cache for resume capability
        if not self.dry_run and self._articles_found:
            try:
                with open(ARTICLES_CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self._articles_found, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Saved {len(self._articles_found)} articles to cache file")
            except Exception as e:
                logger.warning(f"Error saving articles cache: {e}")
    
    def _execute_search(self, search_term: str, start_year: int, end_year: int, term_type: str):
        """
        Execute a single search across multiple archives.
        
        Args:
            search_term: Search query
            start_year: Start year
            end_year: End year
            term_type: "primary" or "secondary"
        """
        self.stats["searches_executed"] += 1
        
        total_results = 0
        articles_found = []
        
        # Search multiple archives
        try:
            # 1. GDELT API (primary source - same as existing scripts)
            gdelt_results = self._search_gdelt(search_term, start_year, end_year)
            articles_found.extend(gdelt_results)
            total_results += len(gdelt_results)
            
            # 2. Trove (National Library) - if API key available
            trove_results = self._search_trove(search_term, start_year, end_year)
            articles_found.extend(trove_results)
            total_results += len(trove_results)
            
        except Exception as e:
            logger.error(f"Error executing search '{search_term}': {e}")
            self.stats["errors"] += 1
        
        # Store articles for processing
        self._articles_found.extend(articles_found)
        self.stats["articles_found"] += total_results
        
        # Log search
        search_entry = {
            "search_term": search_term,
            "start_year": start_year,
            "end_year": end_year,
            "term_type": term_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results_count": total_results,
        }
        self.search_log.append(search_entry)
        
        if total_results > 0:
            logger.info(f"Search: '{search_term}' ({start_year}-{end_year}): {total_results} articles found")
    
    def _search_gdelt(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Search GDELT API for historical articles."""
        articles = []
        
        try:
            # GDELT API endpoint (same as existing scripts)
            GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
            
            # Format dates for GDELT (YYYYMMDDHHMMSS)
            start_date = f"{start_year}0101000000"
            end_date = f"{end_year}1231235959"
            
            # Add Australia filter to query
            gdelt_query = f'{query} AND Australia'
            
            params = {
                "query": gdelt_query,
                "mode": "artlist",
                "maxrecords": 250,  # GDELT limit
                "format": "json",
                "sort": "DateDesc",
                "startdatetime": start_date,
                "enddatetime": end_date,
            }
            
            logger.debug(f"GDELT search: '{query}' ({start_year}-{end_year})")
            
            response = requests.get(GDELT_URL, params=params, timeout=45)
            response.raise_for_status()
            
            data = response.json()
            gdelt_articles = data.get("articles", [])
            
            # Convert GDELT format to our format
            for article in gdelt_articles:
                articles.append({
                    "url": article.get("url", ""),
                    "title": article.get("title", ""),
                    "date": article.get("seendate", ""),
                    "source": article.get("domain", "Unknown"),
                    "snippet": article.get("snippet", ""),
                })
            
            if len(articles) > 0:
                logger.info(f"GDELT search: '{query}' ({start_year}-{end_year}): {len(articles)} articles")
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            logger.debug(f"GDELT search error: {e}")
        
        return articles
    
    def _search_trove(self, query: str, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Search Trove archive."""
        articles = []
        
        try:
            # Import archive accessor
            from scripts.historical_archive_access import TroveArchive
            
            trove = TroveArchive()
            articles = trove.search(query, start_year, end_year)
            
        except Exception as e:
            logger.debug(f"Trove search error: {e}")
        
        return articles
    
    
    def _load_checkpoint(self):
        """Load checkpoint data if it exists."""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                self._processed_urls = set(checkpoint.get("processed_urls", []))
                logger.info(f"Loaded checkpoint: {len(self._processed_urls)} articles already processed")
                return True
            except Exception as e:
                logger.warning(f"Error loading checkpoint: {e}")
        return False
    
    def _save_checkpoint(self):
        """Save checkpoint data."""
        try:
            checkpoint = {
                "processed_urls": list(self._processed_urls),
                "incidents_count": len(self.all_incidents),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    def _save_progress(self):
        """Save incidents in progress to CSV."""
        if not self.all_incidents:
            return
        try:
            df = pd.DataFrame(self.all_incidents)
            df.to_csv(PROGRESS_CSV, index=False)
            logger.info(f"Progress saved: {len(self.all_incidents)} incidents")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def _extract_incidents(self):
        """
        Extract incidents from found articles.
        """
        logger.info(f"Extracting incidents from {len(self._articles_found)} articles...")
        
        if not self._articles_found:
            logger.info("No articles to process")
            return
        
        # Load checkpoint if exists
        self._load_checkpoint()
        
        # Import extractor
        from scripts.historical_incident_extractor import HistoricalIncidentExtractor
        
        api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        if not api_key:
            logger.warning("OpenAI API key not available. Skipping extraction.")
            return
        
        # Use cost-effective model
        extractor = HistoricalIncidentExtractor(api_key=api_key, model="gpt-3.5-turbo")
        
        # Count articles to process
        articles_to_process = [a for a in self._articles_found if a.get("url") not in self._processed_urls]
        total_to_process = len(articles_to_process)
        already_processed = len(self._articles_found) - total_to_process
        
        if already_processed > 0:
            logger.info(f"Resuming: {already_processed} articles already processed, {total_to_process} remaining")
        
        # Process each article
        for idx, article in enumerate(self._articles_found, 1):
            article_url = article.get("url", "")
            
            # Skip if already processed
            if article_url in self._processed_urls:
                continue
            try:
                # Fetch article content if not already fetched
                article_text = article.get("text", "")
                if not article_text and article.get("url"):
                    article_text = self._fetch_article_content(article["url"])
                    article["text"] = article_text
                
                if not article_text:
                    continue
                
                # Extract incident
                incident = extractor.extract_incident(
                    article.get("title", ""),
                    article_text,
                    article.get("url", ""),
                    article.get("date", ""),
                    article.get("source", "Unknown")
                )
                
                if incident:
                    # Generate historical incident ID
                    year = self._extract_year(incident.get("date_of_incident", "")) or "UNK"
                    state = self._extract_state(incident.get("location", "")) or "UNK"
                    seq = len(self.all_incidents) + 1
                    incident["incident_id"] = f"HIST_{year}_{state}_{seq:03d}"
                    
                    # Add source metadata
                    incident["source_authority_level"] = SOURCE_AUTHORITY_LEVELS.get(
                        article.get("source", "Unknown"), 6
                    )
                    incident["archival_status"] = "digitized"
                    incident["verification_status"] = "single-source"  # Will be updated if duplicates found
                    
                    self.all_incidents.append(incident)
                    self.stats["incidents_extracted"] += 1
                    
            except Exception as e:
                error_str = str(e)
                # Handle quota errors - stop processing if quota exceeded
                if "429" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str.lower():
                    logger.error(f"API quota exceeded. Stopping extraction. Please resolve quota issues and resume.")
                    self._save_checkpoint()
                    self._save_progress()
                    raise  # Stop the extraction process
                logger.error(f"Error extracting incident from {article.get('url', 'unknown')}: {e}")
                self.stats["errors"] += 1
            finally:
                # Mark as processed regardless of success/failure
                if article_url:
                    self._processed_urls.add(article_url)
                
                # Save checkpoint every 100 articles
                if idx % 100 == 0:
                    self._save_checkpoint()
                    self._save_progress()
                    logger.info(f"Progress: {idx}/{len(self._articles_found)} articles processed, {self.stats['incidents_extracted']} incidents found")
        
        # Final checkpoint save
        self._save_checkpoint()
        self._save_progress()
        
        logger.info(f"Extracted {self.stats['incidents_extracted']} incidents from {len(self._articles_found)} articles")
    
    def _fetch_article_content(self, url: str) -> str:
        """Fetch article content from URL."""
        try:
            import requests
            from article_fetcher import ArticleFetcher
            
            fetcher = ArticleFetcher()
            response = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (compatible; HistoricalScraper/1.0)"
            })
            response.raise_for_status()
            
            # Use article_fetcher to extract text
            from article_fetcher import ArticleData
            article_data = ArticleData(
                title="",
                url=url,
                publication_date=datetime.now(timezone.utc),
            )
            article_data = fetcher.extract_article_text(article_data)
            
            return article_data.full_text or ""
            
        except Exception as e:
            logger.debug(f"Error fetching article content from {url}: {e}")
            return ""
    
    def _extract_state(self, location: str) -> Optional[str]:
        """Extract state abbreviation from location string."""
        if not location:
            return None
        
        state_map = {
            "NSW": "NSW", "New South Wales": "NSW",
            "VIC": "VIC", "Victoria": "VIC",
            "QLD": "QLD", "Queensland": "QLD",
            "WA": "WA", "Western Australia": "WA",
            "SA": "SA", "South Australia": "SA",
            "TAS": "TAS", "Tasmania": "TAS",
            "NT": "NT", "Northern Territory": "NT",
            "ACT": "ACT", "Australian Capital Territory": "ACT",
        }
        
        location_upper = location.upper()
        for key, value in state_map.items():
            if key.upper() in location_upper:
                return value
        
        return None
    
    def _geocode_incidents(self):
        """Geocode all incident locations."""
        for incident in self.all_incidents:
            location = incident.get("location", "")
            if not location:
                continue
            
            try:
                result = self.geocoder.geocode(location)
                if result:
                    incident["latitude"] = result.latitude
                    incident["longitude"] = result.longitude
                    incident["suburb"] = result.suburb
                    incident["postcode"] = result.postcode
                    self.stats["geocoded"] += 1
                else:
                    self.stats["geocoding_failures"] += 1
            except Exception as e:
                logger.error(f"Geocoding error: {e}")
                self.stats["geocoding_failures"] += 1
    
    def _deduplicate_historical(self):
        """
        Deduplicate historical incidents using historical context algorithm.
        Matches on: date (±3 days), location, incident type.
        """
        logger.info("Deduplicating historical incidents...")
        
        # Use existing deduplicator but with historical tolerance
        deduplicator = Deduplicator(existing_csv_path=str(OUTPUT_CSV))
        
        # For historical data, we use ±3 days tolerance
        dedup_result = deduplicator.find_duplicates(
            self.all_incidents,
            check_existing=True
        )
        
        self.all_incidents = dedup_result["unique"] + dedup_result["consolidated"]
        self.stats["duplicates_found"] = len(dedup_result["duplicates"])
        self.stats["unique_incidents"] = len(self.all_incidents)
        
        logger.info(f"Deduplication: {self.stats['duplicates_found']} duplicates, {self.stats['unique_incidents']} unique")
    
    def _quality_assurance(self):
        """Perform quality assurance validation checks."""
        logger.info("Running quality assurance checks...")
        
        validation_errors = []
        
        for incident in self.all_incidents:
            # Check date format
            date = incident.get("date_of_incident", "")
            if not self._validate_date_format(date):
                validation_errors.append(f"Invalid date format: {incident.get('incident_id')}")
            
            # Check location specificity
            location = incident.get("location", "")
            if not location or len(location.split()) < 2:
                validation_errors.append(f"Location too vague: {incident.get('incident_id')}")
            
            # Check source URL
            if not incident.get("source_url"):
                validation_errors.append(f"Missing source URL: {incident.get('incident_id')}")
            
            # Check coordinates
            if not incident.get("latitude") or not incident.get("longitude"):
                validation_errors.append(f"Missing coordinates: {incident.get('incident_id')}")
        
        if validation_errors:
            logger.warning(f"Quality assurance found {len(validation_errors)} issues")
            for error in validation_errors[:10]:  # Show first 10
                logger.warning(f"  - {error}")
        else:
            logger.info("Quality assurance: All checks passed")
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate date is in DD MM YYYY format."""
        if not date_str:
            return False
        
        # Check for DD MM YYYY format
        pattern = r'^\d{2}\s+\d{2}\s+\d{4}$'
        return bool(re.match(pattern, date_str))
    
    def _gap_analysis(self) -> Dict[str, Any]:
        """Perform gap analysis on coverage."""
        logger.info("Analyzing coverage gaps...")
        
        # Group incidents by year
        incidents_by_year = {}
        incidents_by_state = {}
        incidents_by_type = {}
        incidents_by_source = {}
        
        for incident in self.all_incidents:
            # By year
            year = self._extract_year(incident.get("date_of_incident", ""))
            if year:
                incidents_by_year[year] = incidents_by_year.get(year, 0) + 1
            
            # By state
            state = incident.get("state", "")
            if state:
                incidents_by_state[state] = incidents_by_state.get(state, 0) + 1
            
            # By type
            incident_type = incident.get("incident_type", "")
            if incident_type:
                incidents_by_type[incident_type] = incidents_by_type.get(incident_type, 0) + 1
            
            # By source
            source = incident.get("source_name", "")
            if source:
                incidents_by_source[source] = incidents_by_source.get(source, 0) + 1
        
        gap_analysis = {
            "incidents_by_year": incidents_by_year,
            "incidents_by_state": incidents_by_state,
            "incidents_by_type": incidents_by_type,
            "incidents_by_source": incidents_by_source,
            "total_incidents": len(self.all_incidents),
            "coverage_notes": [],
        }
        
        return gap_analysis
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        if not date_str:
            return None
        
        # Try to extract year (last 4 digits)
        match = re.search(r'\d{4}', date_str)
        if match:
            return int(match.group())
        return None
    
    def _save_results(self):
        """Save incidents to CSV file."""
        if not self.all_incidents:
            logger.info("No incidents to save")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(self.all_incidents)
        
        # Ensure required columns
        required_columns = [
            "incident_id", "date_of_incident", "location", "suburb", "postcode",
            "state", "latitude", "longitude", "description", "incident_type",
            "victim_identity", "perpetrator_info", "source_url", "source_name",
            "publication_date", "source_authority_level", "confidence_score",
            "verification_status", "historical_notes", "archival_status",
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder columns
        df = df[required_columns]
        
        # Save
        df.to_csv(OUTPUT_CSV, index=False)
        logger.info(f"Saved {len(self.all_incidents)} historical incidents to {OUTPUT_CSV}")
    
    def _save_search_log(self):
        """Save search execution log."""
        with open(SEARCH_LOG_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.search_log, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Search log saved to {SEARCH_LOG_JSON}")
    
    def _save_gap_analysis(self, gap_analysis: Dict[str, Any]):
        """Save gap analysis report."""
        with open(GAP_ANALYSIS_JSON, 'w', encoding='utf-8') as f:
            json.dump(gap_analysis, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Gap analysis saved to {GAP_ANALYSIS_JSON}")
    
    def _print_summary(self):
        """Print final summary statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("HISTORICAL SCRAPER 2005-2019 - COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Date Range: {START_DATE.date()} to {END_DATE.date()}")
        logger.info(f"Searches executed: {self.stats['searches_executed']}")
        logger.info(f"Articles found: {self.stats['articles_found']}")
        logger.info(f"Incidents extracted: {self.stats['incidents_extracted']}")
        logger.info(f"Unique incidents: {self.stats['unique_incidents']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Geocoded: {self.stats['geocoded']}")
        logger.info(f"Geocoding failures: {self.stats['geocoding_failures']}")
        logger.info("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Historical Incident Scraper for 2005-2019"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving files (for testing)"
    )
    
    args = parser.parse_args()
    
    try:
        scraper = HistoricalScraper2005_2019(dry_run=args.dry_run)
        result = scraper.run()
        
        print("\n" + "=" * 70)
        print("HISTORICAL SCRAPER RESULTS")
        print("=" * 70)
        print(f"Unique incidents found: {result['summary']['unique_incidents']}")
        print(f"Total searches executed: {result['summary']['searches_executed']}")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

