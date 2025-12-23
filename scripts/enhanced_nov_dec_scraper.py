"""
Enhanced Incident Scraper for November-December 2025
Section 1.1: Automated Incident Scraper Execution & Validation

This script:
- Scrapes incidents from Nov 1, 2025 to Dec 22, 2025 (52 days)
- Implements confidence-based filtering (HIGH >85%, MEDIUM 70-85%, LOW <70%)
- Auto-adds HIGH confidence incidents to map
- Creates human review queue for MEDIUM confidence incidents
- Generates comprehensive status reports
"""

import os
import sys
import logging
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Import project config
try:
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
except ImportError:
    OPENAI_API_KEY = None
    RATE_LIMIT_DELAY = 1

# Import RSS monitor modules
from rss_feeds import get_all_feeds
from article_fetcher import ArticleFetcher, ArticleData
from incident_extractor import IncidentExtractor
from geocoder import Geocoder, GeocodeResult
from deduplicator import Deduplicator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "logs" / f"nov_dec_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "incidents_news_sourced.csv"
MAP_CSV = DATA_DIR / "incidents_in_progress.csv"
REVIEW_QUEUE_CSV = DATA_DIR / "review_queue_nov_dec_2025.csv"
REJECTED_CSV = DATA_DIR / "rejected_incidents_nov_dec_2025.csv"
STATUS_REPORT_JSON = DATA_DIR / "nov_dec_2025_status_report.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Date range: Nov 1, 2025 to Dec 22, 2025 (52 days)
START_DATE = datetime(2025, 11, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 12, 22, 23, 59, 59, tzinfo=timezone.utc)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days + 1

# Confidence thresholds
CONFIDENCE_HIGH = 0.85
CONFIDENCE_MEDIUM = 0.70
CONFIDENCE_LOW = 0.70


class EnhancedNovDecScraper:
    """
    Enhanced scraper for November-December 2025 with confidence scoring
    and automated review queue management.
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the enhanced scraper.
        
        Args:
            dry_run: If True, don't save files (for testing)
        """
        self.dry_run = dry_run
        
        # Get API key
        api_key = os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or configure in config.py"
            )
        
        # Initialize components
        self.article_fetcher = ArticleFetcher(rate_limit_delay=RATE_LIMIT_DELAY)
        self.incident_extractor = IncidentExtractor(api_key=api_key)
        self.geocoder = Geocoder(cache_file=str(BASE_DIR / "geocoding_cache.json"))
        
        # Use existing incidents for deduplication
        dedup_csv = MAP_CSV if MAP_CSV.exists() else OUTPUT_CSV
        self.deduplicator = Deduplicator(existing_csv_path=str(dedup_csv))
        
        # Statistics
        self.stats = {
            "feeds_processed": 0,
            "articles_fetched": 0,
            "articles_processed": 0,
            "incidents_extracted": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "geocoded": 0,
            "geocoding_failures": 0,
            "duplicates_found": 0,
            "unique_new": 0,
            "added_to_map": 0,
            "pending_review": 0,
            "rejected": 0,
            "errors": 0,
        }
        
        # Results storage
        self.high_confidence_incidents = []
        self.medium_confidence_incidents = []
        self.low_confidence_incidents = []
        self.geocoding_failures = []
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete scraping pipeline.
        
        Returns:
            Dictionary with results and statistics
        """
        logger.info("=" * 70)
        logger.info("ENHANCED NOV-DEC 2025 SCRAPER")
        logger.info("=" * 70)
        logger.info(f"Date Range: {START_DATE.date()} to {END_DATE.date()} ({DATE_RANGE_DAYS} days)")
        logger.info("=" * 70)
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Step 1: Fetch RSS feeds (filter by date range)
            logger.info("\n[STEP 1] Fetching RSS Feeds...")
            all_articles = self._fetch_all_feeds()
            
            if not all_articles:
                logger.warning("No articles fetched. Exiting.")
                return self._generate_results(start_time)
            
            # Step 2: Extract incidents
            logger.info("\n[STEP 2] Extracting Incidents...")
            incidents = self._extract_incidents(all_articles)
            
            if not incidents:
                logger.info("No incidents found. Exiting.")
                return self._generate_results(start_time)
            
            # Step 3: Classify by confidence
            logger.info("\n[STEP 3] Classifying by Confidence...")
            self._classify_by_confidence(incidents)
            
            # Step 4: Geocode incidents
            logger.info("\n[STEP 4] Geocoding Locations...")
            self._geocode_all_incidents()
            
            # Step 5: Deduplicate HIGH confidence incidents
            logger.info("\n[STEP 5] Deduplicating...")
            self._deduplicate_incidents()
            
            # Step 6: Save results
            logger.info("\n[STEP 6] Saving Results...")
            if not self.dry_run:
                self._save_results()
            else:
                logger.info("[DRY RUN] Skipping file save")
            
            # Step 7: Generate status report
            logger.info("\n[STEP 7] Generating Status Report...")
            status_report = self._generate_status_report(start_time)
            
            if not self.dry_run:
                self._save_status_report(status_report)
            
            # Print summary
            self._print_summary()
            
            return status_report
            
        except Exception as e:
            logger.error(f"Fatal error in scraper: {e}", exc_info=True)
            self.stats["errors"] += 1
            raise
    
    def _fetch_all_feeds(self) -> List[ArticleData]:
        """Fetch articles from all enabled RSS feeds within date range."""
        feeds = get_all_feeds()
        all_articles = []
        
        logger.info(f"Processing {len(feeds)} RSS feeds...")
        
        for feed in feeds:
            try:
                logger.info(f"Fetching: {feed.name}")
                articles = self.article_fetcher.fetch_rss_feed(feed.url, feed.name)
                
                # Filter by date range (Nov 1 - Dec 22, 2025)
                filtered_articles = []
                for article in articles:
                    if START_DATE <= article.publication_date <= END_DATE:
                        filtered_articles.append(article)
                
                # Extract full text for better incident detection
                for article in filtered_articles:
                    article = self.article_fetcher.extract_article_text(article)
                    all_articles.append(article)
                
                self.stats["feeds_processed"] += 1
                self.stats["articles_fetched"] += len(articles)
                self.stats["articles_processed"] += len(filtered_articles)
                logger.info(f"  -> Found {len(filtered_articles)} articles in date range")
                
            except Exception as e:
                logger.error(f"Error processing feed {feed.name}: {e}")
                self.stats["errors"] += 1
                continue
        
        logger.info(f"\nTotal articles in date range: {len(all_articles)}")
        return all_articles
    
    def _extract_incidents(self, articles: List[ArticleData]) -> List[Dict[str, Any]]:
        """Extract incidents from articles using GPT-4."""
        incidents = []
        
        for article in articles:
            try:
                incident = self.incident_extractor.extract_incident(
                    article.title,
                    article.full_text or article.summary or "",
                    article.url
                )
                
                if incident:
                    # Add article metadata
                    incident["article_url"] = article.url
                    incident["article_title"] = article.title
                    incident["publication_date"] = article.publication_date.isoformat()
                    incident["news_source"] = article.source_name or "Unknown"
                    incident["extracted_at"] = datetime.now(timezone.utc).isoformat()
                    
                    # Generate incident ID
                    incident_id = f"INC_{datetime.now().strftime('%Y%m%d')}_{len(incidents) + 1:03d}"
                    incident["incident_id"] = incident_id
                    
                    incidents.append(incident)
                    self.stats["incidents_extracted"] += 1
                    
            except Exception as e:
                logger.error(f"Error extracting incident from {article.url}: {e}")
                self.stats["errors"] += 1
                continue
        
        logger.info(f"Extracted {len(incidents)} incidents from {len(articles)} articles")
        return incidents
    
    def _classify_by_confidence(self, incidents: List[Dict[str, Any]]):
        """Classify incidents by confidence score."""
        for incident in incidents:
            confidence = incident.get("confidence", 0.5)
            
            if confidence >= CONFIDENCE_HIGH:
                self.high_confidence_incidents.append(incident)
                self.stats["high_confidence"] += 1
            elif confidence >= CONFIDENCE_MEDIUM:
                self.medium_confidence_incidents.append(incident)
                self.stats["medium_confidence"] += 1
            else:
                self.low_confidence_incidents.append(incident)
                self.stats["low_confidence"] += 1
        
        logger.info(f"Confidence Classification:")
        logger.info(f"  HIGH (≥{CONFIDENCE_HIGH*100:.0f}%): {self.stats['high_confidence']}")
        logger.info(f"  MEDIUM ({CONFIDENCE_MEDIUM*100:.0f}-{CONFIDENCE_HIGH*100:.0f}%): {self.stats['medium_confidence']}")
        logger.info(f"  LOW (<{CONFIDENCE_MEDIUM*100:.0f}%): {self.stats['low_confidence']}")
    
    def _geocode_all_incidents(self):
        """Geocode all incidents and track failures."""
        all_incidents = (
            self.high_confidence_incidents +
            self.medium_confidence_incidents +
            self.low_confidence_incidents
        )
        
        for incident in all_incidents:
            location = incident.get("location", "")
            if not location:
                incident["geocoding_status"] = "NO_LOCATION"
                incident["latitude"] = None
                incident["longitude"] = None
                incident["suburb"] = None
                incident["postcode"] = None
                continue
            
            try:
                result = self.geocoder.geocode(location)
                
                if result:
                    incident["latitude"] = result.latitude
                    incident["longitude"] = result.longitude
                    incident["suburb"] = result.suburb
                    incident["postcode"] = result.postcode
                    incident["geocoding_status"] = "SUCCESS"
                    incident["geocoding_confidence"] = result.confidence
                    self.stats["geocoded"] += 1
                else:
                    incident["geocoding_status"] = "FAILED"
                    incident["latitude"] = None
                    incident["longitude"] = None
                    incident["suburb"] = None
                    incident["postcode"] = None
                    self.stats["geocoding_failures"] += 1
                    self.geocoding_failures.append(incident)
                    
            except Exception as e:
                logger.error(f"Geocoding error for {location}: {e}")
                incident["geocoding_status"] = "ERROR"
                incident["latitude"] = None
                incident["longitude"] = None
                incident["suburb"] = None
                incident["postcode"] = None
                self.stats["geocoding_failures"] += 1
                self.stats["errors"] += 1
                self.geocoding_failures.append(incident)
        
        logger.info(f"Geocoded {self.stats['geocoded']}/{len(all_incidents)} incidents")
        logger.info(f"Geocoding failures: {self.stats['geocoding_failures']}")
    
    def _deduplicate_incidents(self):
        """Deduplicate HIGH confidence incidents before adding to map."""
        if not self.high_confidence_incidents:
            logger.info("No HIGH confidence incidents to deduplicate")
            return
        
        dedup_result = self.deduplicator.find_duplicates(
            self.high_confidence_incidents,
            check_existing=True
        )
        
        # Update HIGH confidence list with unique incidents only
        self.high_confidence_incidents = dedup_result["unique"] + dedup_result["consolidated"]
        self.stats["duplicates_found"] = len(dedup_result["duplicates"])
        self.stats["unique_new"] = len(self.high_confidence_incidents)
        
        logger.info(f"Deduplication: {self.stats['duplicates_found']} duplicates, {self.stats['unique_new']} unique")
    
    def _save_results(self):
        """Save incidents to appropriate files based on confidence."""
        # Save HIGH confidence incidents to map CSV
        if self.high_confidence_incidents:
            self._save_to_map_csv(self.high_confidence_incidents)
            self.stats["added_to_map"] = len(self.high_confidence_incidents)
        
        # Save MEDIUM confidence incidents to review queue
        if self.medium_confidence_incidents:
            self._save_to_review_queue(self.medium_confidence_incidents)
            self.stats["pending_review"] = len(self.medium_confidence_incidents)
        
        # Save LOW confidence incidents to rejected file
        if self.low_confidence_incidents:
            self._save_to_rejected(self.low_confidence_incidents)
            self.stats["rejected"] = len(self.low_confidence_incidents)
    
    def _save_to_map_csv(self, incidents: List[Dict[str, Any]]):
        """Save HIGH confidence incidents to map CSV (incidents_in_progress.csv)."""
        formatted_rows = self._convert_to_project_format(incidents)
        
        # Load existing data
        if MAP_CSV.exists():
            df_existing = pd.read_csv(MAP_CSV)
            logger.info(f"Loaded {len(df_existing)} existing incidents from map CSV")
        else:
            df_existing = pd.DataFrame()
            logger.info("Creating new map CSV file")
        
        # Create DataFrame from new incidents
        df_new = pd.DataFrame(formatted_rows)
        
        # Combine
        if len(df_existing) > 0:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Save
        df_combined.to_csv(MAP_CSV, index=False)
        logger.info(f"Saved {len(formatted_rows)} HIGH confidence incidents to {MAP_CSV}")
        logger.info(f"Total incidents in map: {len(df_combined)}")
    
    def _save_to_review_queue(self, incidents: List[Dict[str, Any]]):
        """Save MEDIUM confidence incidents to review queue CSV."""
        review_data = []
        
        for incident in incidents:
            review_data.append({
                "incident_id": incident.get("incident_id", ""),
                "review_status": "PENDING_REVIEW",
                "confidence_score": incident.get("confidence", 0.0),
                "date_of_incident": incident.get("date_of_incident", ""),
                "location": incident.get("location", ""),
                "suburb": incident.get("suburb", ""),
                "postcode": incident.get("postcode", ""),
                "incident_type": incident.get("incident_type", ""),
                "victim_identity": incident.get("victim_identity", ""),
                "description": incident.get("description", ""),
                "article_url": incident.get("article_url", ""),
                "article_title": incident.get("article_title", ""),
                "news_source": incident.get("news_source", ""),
                "geocoding_status": incident.get("geocoding_status", ""),
                "geocoding_confidence": incident.get("geocoding_confidence", ""),
                "extracted_at": incident.get("extracted_at", ""),
                "review_notes": "",
            })
        
        df_review = pd.DataFrame(review_data)
        df_review.to_csv(REVIEW_QUEUE_CSV, index=False)
        logger.info(f"Saved {len(review_data)} incidents to review queue: {REVIEW_QUEUE_CSV}")
    
    def _save_to_rejected(self, incidents: List[Dict[str, Any]]):
        """Save LOW confidence incidents to rejected file."""
        rejected_data = []
        
        for incident in incidents:
            rejected_data.append({
                "incident_id": incident.get("incident_id", ""),
                "review_status": "REJECTED_LOW_CONFIDENCE",
                "confidence_score": incident.get("confidence", 0.0),
                "rejection_reason": "Confidence score below threshold",
                "date_of_incident": incident.get("date_of_incident", ""),
                "location": incident.get("location", ""),
                "incident_type": incident.get("incident_type", ""),
                "description": incident.get("description", ""),
                "article_url": incident.get("article_url", ""),
                "extracted_at": incident.get("extracted_at", ""),
            })
        
        df_rejected = pd.DataFrame(rejected_data)
        df_rejected.to_csv(REJECTED_CSV, index=False)
        logger.info(f"Saved {len(rejected_data)} rejected incidents to {REJECTED_CSV}")
    
    def _convert_to_project_format(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert incidents to project CSV format."""
        formatted_rows = []
        
        for incident in incidents:
            # Parse date
            incident_date = incident.get("date_of_incident")
            if incident_date:
                try:
                    dt = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
                    incident_date = dt.strftime("%Y%m%dT%H%M%SZ")
                except:
                    pass
            
            # Format publication date
            pub_date = incident.get("publication_date", "")
            if pub_date:
                try:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    pub_date = dt.strftime("%Y%m%dT%H%M%SZ")
                except:
                    pass
            
            row = {
                "title": incident.get("article_title", ""),
                "url": incident.get("article_url", ""),
                "source_date": pub_date,
                "incident_type": incident.get("incident_type", "other"),
                "date": incident_date,
                "location": incident.get("location", ""),
                "victim_identity": incident.get("victim_identity", "unknown"),
                "description": incident.get("description", ""),
                "severity": self._estimate_severity(incident.get("incident_type")),
                "perpetrator_info": None,
                "latitude": incident.get("latitude"),
                "longitude": incident.get("longitude"),
                "confidence_score": incident.get("confidence", 0.0),
                "review_status": "APPROVED",
                "added_to_map_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "notes": f"Auto-added (HIGH confidence: {incident.get('confidence', 0.0):.2%})",
            }
            
            formatted_rows.append(row)
        
        return formatted_rows
    
    def _estimate_severity(self, incident_type: Optional[str]) -> str:
        """Estimate severity based on incident type."""
        if not incident_type:
            return "medium"
        
        high_severity = {"assault", "sexual_violence", "threat"}
        medium_severity = {"harassment", "vandalism", "discrimination"}
        
        if incident_type in high_severity:
            return "high"
        elif incident_type in medium_severity:
            return "medium"
        else:
            return "low"
    
    def _generate_status_report(self, start_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        # Calculate geocoding failure rate
        total_geocoding_attempts = self.stats["geocoded"] + self.stats["geocoding_failures"]
        geocoding_failure_rate = (
            (self.stats["geocoding_failures"] / total_geocoding_attempts * 100)
            if total_geocoding_attempts > 0 else 0
        )
        
        # Calculate medium confidence percentage
        total_incidents = self.stats["incidents_extracted"]
        medium_confidence_rate = (
            (self.stats["medium_confidence"] / total_incidents * 100)
            if total_incidents > 0 else 0
        )
        
        # Group by state/territory
        incidents_by_state = {}
        for incident in self.high_confidence_incidents + self.medium_confidence_incidents:
            state = incident.get("suburb", "").split()[-1] if incident.get("suburb") else "Unknown"
            incidents_by_state[state] = incidents_by_state.get(state, 0) + 1
        
        # Group by category
        incidents_by_category = {}
        for incident in self.high_confidence_incidents + self.medium_confidence_incidents:
            category = incident.get("incident_type", "unknown")
            incidents_by_category[category] = incidents_by_category.get(category, 0) + 1
        
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
                "total_incidents_scraped": self.stats["incidents_extracted"],
                "unique_incidents_after_dedup": self.stats["unique_new"],
                "added_to_map_high_confidence": self.stats["added_to_map"],
                "pending_human_review_medium_confidence": self.stats["pending_review"],
                "rejected_archived_low_confidence": self.stats["rejected"],
                "geocoding_failures": self.stats["geocoding_failures"],
                "geocoding_failure_rate_percent": round(geocoding_failure_rate, 2),
                "medium_confidence_rate_percent": round(medium_confidence_rate, 2),
            },
            "incidents_by_state": incidents_by_state,
            "incidents_by_category": incidents_by_category,
            "statistics": self.stats.copy(),
            "alerts": {
                "geocoding_failure_rate_high": geocoding_failure_rate > 10,
                "medium_confidence_rate_high": medium_confidence_rate > 30,
                "scraper_failed": self.stats["errors"] > self.stats["feeds_processed"],
            },
            "review_queue_info": {
                "pending_count": self.stats["pending_review"],
                "review_queue_file": str(REVIEW_QUEUE_CSV),
                "email_alert_required": self.stats["pending_review"] > 0,
            }
        }
        
        return report
    
    def _save_status_report(self, report: Dict[str, Any]):
        """Save status report to JSON file."""
        with open(STATUS_REPORT_JSON, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Status report saved to {STATUS_REPORT_JSON}")
    
    def _generate_results(self, start_time: datetime) -> Dict[str, Any]:
        """Generate results dictionary even if no incidents found."""
        return self._generate_status_report(start_time)
    
    def _print_summary(self):
        """Print final summary statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("ENHANCED NOV-DEC 2025 SCRAPER - COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Date Range: {START_DATE.date()} to {END_DATE.date()}")
        logger.info(f"Feeds processed: {self.stats['feeds_processed']}")
        logger.info(f"Articles fetched: {self.stats['articles_fetched']}")
        logger.info(f"Articles in date range: {self.stats['articles_processed']}")
        logger.info(f"Incidents extracted: {self.stats['incidents_extracted']}")
        logger.info(f"  → HIGH confidence (≥{CONFIDENCE_HIGH*100:.0f}%): {self.stats['high_confidence']}")
        logger.info(f"  → MEDIUM confidence ({CONFIDENCE_MEDIUM*100:.0f}-{CONFIDENCE_HIGH*100:.0f}%): {self.stats['medium_confidence']}")
        logger.info(f"  → LOW confidence (<{CONFIDENCE_MEDIUM*100:.0f}%): {self.stats['low_confidence']}")
        logger.info(f"Geocoded: {self.stats['geocoded']}")
        logger.info(f"Geocoding failures: {self.stats['geocoding_failures']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Unique new incidents: {self.stats['unique_new']}")
        logger.info(f"Added to map (HIGH): {self.stats['added_to_map']}")
        logger.info(f"Pending review (MEDIUM): {self.stats['pending_review']}")
        logger.info(f"Rejected (LOW): {self.stats['rejected']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhanced Incident Scraper for Nov-Dec 2025"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving files (for testing)"
    )
    
    args = parser.parse_args()
    
    try:
        scraper = EnhancedNovDecScraper(dry_run=args.dry_run)
        result = scraper.run()
        
        # Print key metrics
        print("\n" + "=" * 70)
        print("KEY METRICS")
        print("=" * 70)
        print(f"Total incidents scraped: {result['summary']['total_incidents_scraped']}")
        print(f"Added to map (HIGH confidence): {result['summary']['added_to_map_high_confidence']}")
        print(f"Pending review (MEDIUM confidence): {result['summary']['pending_human_review_medium_confidence']}")
        print(f"Rejected (LOW confidence): {result['summary']['rejected_archived_low_confidence']}")
        print(f"Geocoding failure rate: {result['summary']['geocoding_failure_rate_percent']:.1f}%")
        print("=" * 70)
        
        if result['alerts']['geocoding_failure_rate_high']:
            print("⚠️  ALERT: Geocoding failure rate > 10%")
        if result['alerts']['medium_confidence_rate_high']:
            print("⚠️  ALERT: Medium confidence incidents > 30%")
        if result['alerts']['scraper_failed']:
            print("❌ ALERT: Scraper encountered errors")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

