"""
Main RSS Monitor Orchestrator

This module orchestrates the complete RSS feed monitoring pipeline:
1. Fetch RSS feeds
2. Extract articles
3. Identify incidents
4. Geocode locations
5. Deduplicate
6. Save to CSV
7. Prepare for GitHub commit

Designed to run as a daily cron job via GitHub Actions.
"""

import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Import config from project root (same directory)
try:
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
except ImportError:
    OPENAI_API_KEY = None
    RATE_LIMIT_DELAY = 1

# Import our modules
from rss_feeds import get_all_feeds, RSSFeed
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
    ]
)
logger = logging.getLogger(__name__)


# Configuration
DATA_DIR = Path("data")
OUTPUT_CSV = DATA_DIR / "incidents_news_sourced.csv"
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class RSSMonitor:
    """
    Main orchestrator for RSS feed monitoring and incident extraction.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        hours_back: int = 24,
        dry_run: bool = False,
    ):
        """
        Initialize the RSS Monitor.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            hours_back: How many hours of articles to fetch (default: 24)
            dry_run: If True, don't save files (for testing)
        """
        self.hours_back = hours_back
        self.dry_run = dry_run
        
        # Initialize components
        self.article_fetcher = ArticleFetcher(rate_limit_delay=RATE_LIMIT_DELAY)
        self.incident_extractor = IncidentExtractor(api_key=api_key or OPENAI_API_KEY)
        self.geocoder = Geocoder(cache_file="geocoding_cache.json")
        self.deduplicator = Deduplicator(existing_csv_path=str(OUTPUT_CSV))
        
        # Statistics
        self.stats = {
            "feeds_processed": 0,
            "articles_fetched": 0,
            "incidents_extracted": 0,
            "geocoded": 0,
            "duplicates_found": 0,
            "unique_new": 0,
            "errors": 0,
        }
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete monitoring pipeline.
        
        Returns:
            Dictionary with statistics and results
        """
        logger.info("=" * 70)
        logger.info("RSS MONITOR - Starting Daily Feed Monitoring")
        logger.info("=" * 70)
        
        start_time = datetime.now(timezone.utc)
        
        # Step 1: Fetch all RSS feeds
        logger.info("\n[STEP 1] Fetching RSS Feeds...")
        all_articles = self._fetch_all_feeds()
        
        # Step 2: Extract incidents from articles
        logger.info("\n[STEP 2] Extracting Incidents...")
        incidents = self._extract_incidents(all_articles)
        
        # Step 3: Geocode incidents
        logger.info("\n[STEP 3] Geocoding Locations...")
        geocoded_incidents = self._geocode_incidents(incidents)
        
        # Step 4: Deduplicate
        logger.info("\n[STEP 4] Deduplicating Incidents...")
        dedup_result = self.deduplicator.find_duplicates(geocoded_incidents)
        
        # Step 5: Save to CSV
        logger.info("\n[STEP 5] Saving Results...")
        if not self.dry_run:
            self._save_results(dedup_result)
        else:
            logger.info("[DRY RUN] Skipping file save")
        
        # Final statistics
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        self.stats.update({
            "unique_new": len(dedup_result["unique"]),
            "duplicates_found": len(dedup_result["duplicates"]),
            "duration_seconds": duration,
        })
        
        logger.info("\n" + "=" * 70)
        logger.info("RSS MONITOR - Complete")
        logger.info("=" * 70)
        logger.info(f"Feeds processed: {self.stats['feeds_processed']}")
        logger.info(f"Articles fetched: {self.stats['articles_fetched']}")
        logger.info(f"Incidents extracted: {self.stats['incidents_extracted']}")
        logger.info(f"Geocoded: {self.stats['geocoded']}")
        logger.info(f"Unique new incidents: {self.stats['unique_new']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Duration: {duration:.1f} seconds")
        logger.info("=" * 70)
        
        return {
            "stats": self.stats,
            "unique_incidents": dedup_result["unique"],
            "duplicates": dedup_result["duplicates"],
            "consolidated": dedup_result["consolidated"],
        }
    
    def _fetch_all_feeds(self) -> List[ArticleData]:
        """Fetch articles from all enabled RSS feeds."""
        feeds = get_all_feeds()
        all_articles = []
        
        logger.info(f"Processing {len(feeds)} RSS feeds...")
        
        for feed in feeds:
            try:
                logger.info(f"Fetching: {feed.name}")
                articles = self.article_fetcher.fetch_rss_feed(feed.url, feed.name)
                
                # Filter by time window
                articles = self.article_fetcher.filter_recent_articles(articles, self.hours_back)
                
                # Extract full text (for better incident detection)
                for article in articles:
                    article = self.article_fetcher.extract_article_text(article)
                    all_articles.append(article)
                
                self.stats["feeds_processed"] += 1
                self.stats["articles_fetched"] += len(articles)
                logger.info(f"  → Found {len(articles)} articles from last {self.hours_back} hours")
                
            except Exception as e:
                logger.error(f"Error processing feed {feed.name}: {e}")
                self.stats["errors"] += 1
                continue
        
        logger.info(f"\nTotal articles fetched: {len(all_articles)}")
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
                    incident["publication_date"] = article.publication_date.isoformat()
                    incident["news_source"] = article.source_name or "Unknown"
                    incident["verification_status"] = "pending"
                    incident["notes"] = None
                    
                    # Generate incident_id (simple hash of URL + date)
                    incident_id = abs(hash(f"{article.url}{incident.get('date_of_incident', '')}")) % 1000000
                    incident["incident_id"] = incident_id
                    
                    incidents.append(incident)
                    self.stats["incidents_extracted"] += 1
                    
            except Exception as e:
                logger.error(f"Error extracting incident from {article.url}: {e}")
                self.stats["errors"] += 1
                continue
        
        logger.info(f"Extracted {len(incidents)} incidents from {len(articles)} articles")
        return incidents
    
    def _geocode_incidents(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Geocode locations for all incidents."""
        geocoded = []
        
        for incident in incidents:
            location = incident.get("location", "")
            if not location:
                logger.warning(f"No location for incident {incident.get('incident_id')}")
                geocoded.append(incident)
                continue
            
            try:
                result = self.geocoder.geocode(location)
                
                if result:
                    incident["suburb"] = result.suburb
                    incident["postcode"] = result.postcode
                    incident["latitude"] = result.latitude
                    incident["longitude"] = result.longitude
                    self.stats["geocoded"] += 1
                else:
                    incident["suburb"] = None
                    incident["postcode"] = None
                    incident["latitude"] = None
                    incident["longitude"] = None
                    logger.warning(f"Could not geocode: {location}")
                
            except Exception as e:
                logger.error(f"Geocoding error for {location}: {e}")
                self.stats["errors"] += 1
                incident["suburb"] = None
                incident["postcode"] = None
                incident["latitude"] = None
                incident["longitude"] = None
            
            geocoded.append(incident)
        
        logger.info(f"Geocoded {self.stats['geocoded']}/{len(incidents)} incidents")
        return geocoded
    
    def _save_results(self, dedup_result: Dict[str, Any]):
        """Save unique incidents to CSV file."""
        unique_incidents = dedup_result["unique"]
        consolidated = dedup_result["consolidated"]
        
        # Combine unique and consolidated incidents
        all_new_incidents = unique_incidents + consolidated
        
        if not all_new_incidents:
            logger.info("No new incidents to save")
            return
        
        # Convert to DataFrame with required columns
        df_new = pd.DataFrame(all_new_incidents)
        
        # Ensure required columns exist
        required_columns = [
            "incident_id",
            "date_of_incident",
            "incident_type",
            "victim_identity",
            "location",
            "suburb",
            "postcode",
            "latitude",
            "longitude",
            "description",
            "article_url",
            "publication_date",
            "news_source",
            "verification_status",
            "notes",
        ]
        
        for col in required_columns:
            if col not in df_new.columns:
                df_new[col] = None
        
        # Reorder columns
        df_new = df_new[required_columns]
        
        # Load existing CSV if it exists
        if OUTPUT_CSV.exists():
            df_existing = pd.read_csv(OUTPUT_CSV)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Save to CSV
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df_combined.to_csv(OUTPUT_CSV, index=False)
        
        logger.info(f"Saved {len(all_new_incidents)} new incidents to {OUTPUT_CSV}")
        logger.info(f"Total incidents in database: {len(df_combined)}")
        
        # Save deduplication report
        report_path = LOG_DIR / f"dedup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.deduplicator.save_dedup_report(dedup_result, str(report_path))


def main():
    """Main entry point for the RSS monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="RSS Monitor for LGBTIQ+ Hate Crime Incidents"
    )
    parser.add_argument(
        "--hours-back",
        type=int,
        default=24,
        help="How many hours of articles to fetch (default: 24)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving files (for testing)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (defaults to OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get API key from args, config, or environment
    api_key = args.api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key required. Set OPENAI_API_KEY in config.py, environment variable, or use --api-key")
        sys.exit(1)
    
    # Run monitor
    monitor = RSSMonitor(
        api_key=api_key,
        hours_back=args.hours_back,
        dry_run=args.dry_run,
    )
    
    result = monitor.run()
    
    # Exit with error code if there were too many errors
    if monitor.stats["errors"] > monitor.stats["feeds_processed"]:
        logger.error("Too many errors occurred during processing")
        sys.exit(1)


if __name__ == "__main__":
    main()
