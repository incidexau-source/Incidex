"""
RSS Monitor for LGBTIQ+ Hate Crime Incidents

This script monitors RSS feeds from Australian news outlets, extracts
LGBTIQ+ hate crime incidents, geocodes them, and adds them to the incident
database. Designed to run daily via GitHub Actions.

Usage:
    python scripts/rss_monitor.py

Environment Variables:
    OPENAI_API_KEY: OpenAI API key (required)
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import pandas as pd

# Import project config
try:
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
except ImportError:
    OPENAI_API_KEY = None
    RATE_LIMIT_DELAY = 1

# Import RSS monitor modules (from project root)
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
    ]
)
logger = logging.getLogger(__name__)


# Paths
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "incidents_news_sourced.csv"
EXISTING_CSV = DATA_DIR / "incidents_extracted.csv"  # Main incidents file to check against

# Also check against the RSS-sourced CSV for deduplication
RSS_SOURCED_CSV = DATA_DIR / "incidents_news_sourced.csv"


class RSSMonitorScript:
    """
    Main RSS monitoring script for GitHub Actions.
    
    Handles:
    - RSS feed fetching
    - Incident extraction
    - Geocoding
    - Deduplication
    - CSV updates
    - Git commits
    """
    
    def __init__(self, hours_back: int = 24, dry_run: bool = False):
        """
        Initialize the RSS monitor script.
        
        Args:
            hours_back: How many hours of articles to fetch
            dry_run: If True, don't save files or commit
        """
        self.hours_back = hours_back
        self.dry_run = dry_run
        
        # Get API key from environment or config
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
        # Check both existing CSVs for deduplication
        # Use the RSS-sourced CSV if it exists, otherwise the main incidents CSV
        dedup_csv = RSS_SOURCED_CSV if RSS_SOURCED_CSV.exists() else EXISTING_CSV
        self.deduplicator = Deduplicator(existing_csv_path=str(dedup_csv))
        
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
    
    def run(self) -> int:
        """
        Run the complete RSS monitoring pipeline.
        
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            logger.info("=" * 70)
            logger.info("RSS MONITOR - Starting Daily Feed Monitoring")
            logger.info("=" * 70)
            
            start_time = datetime.now(timezone.utc)
            
            # Step 1: Fetch RSS feeds
            logger.info("\n[STEP 1] Fetching RSS Feeds...")
            all_articles = self._fetch_all_feeds()
            
            if not all_articles:
                logger.warning("No articles fetched. Exiting.")
                return 0
            
            # Step 2: Extract incidents
            logger.info("\n[STEP 2] Extracting Incidents...")
            incidents = self._extract_incidents(all_articles)
            
            if not incidents:
                logger.info("No incidents found. Exiting.")
                return 0
            
            # Step 3: Geocode incidents
            logger.info("\n[STEP 3] Geocoding Locations...")
            geocoded_incidents = self._geocode_incidents(incidents)
            
            # Step 4: Deduplicate
            logger.info("\n[STEP 4] Deduplicating Incidents...")
            dedup_result = self.deduplicator.find_duplicates(geocoded_incidents)
            
            # Step 5: Convert to project format and save
            logger.info("\n[STEP 5] Saving Results...")
            unique_incidents = dedup_result["unique"]
            consolidated = dedup_result["consolidated"]
            
            if not unique_incidents and not consolidated:
                logger.info("No new unique incidents to save.")
                return 0
            
            # Convert to project CSV format
            new_rows = self._convert_to_project_format(unique_incidents + consolidated)
            
            if not self.dry_run:
                self._save_to_csv(new_rows)
                self._commit_changes()
            else:
                logger.info("[DRY RUN] Skipping file save and commit")
            
            # Final statistics
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            self.stats.update({
                "unique_new": len(unique_incidents) + len(consolidated),
                "duplicates_found": len(dedup_result["duplicates"]),
                "duration_seconds": duration,
            })
            
            self._print_summary()
            
            return 0
            
        except Exception as e:
            logger.error(f"Fatal error in RSS monitor: {e}", exc_info=True)
            return 1
    
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
                
                # Extract full text for better incident detection
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
                    incident["article_title"] = article.title
                    
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
                logger.warning(f"No location for incident from {incident.get('article_url', 'unknown')}")
                incident["latitude"] = None
                incident["longitude"] = None
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
    
    def _convert_to_project_format(self, incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert incidents to project CSV format.
        
        Project format columns:
        title, url, source_date, incident_type, date, location, victim_identity,
        description, severity, perpetrator_info, latitude, longitude
        """
        formatted_rows = []
        
        for incident in incidents:
            # Parse date
            incident_date = incident.get("date_of_incident")
            if not incident_date:
                incident_date = None
            elif isinstance(incident_date, str):
                try:
                    # Try to parse and format
                    dt = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
                    incident_date = dt.strftime("%Y%m%dT%H%M%SZ")
                except:
                    incident_date = incident_date  # Keep as-is
            
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
                "perpetrator_info": None,  # Not extracted by current system
                "latitude": incident.get("latitude"),
                "longitude": incident.get("longitude"),
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
    
    def _save_to_csv(self, new_rows: List[Dict[str, Any]]):
        """Save new incidents to CSV file."""
        if not new_rows:
            logger.info("No new incidents to save")
            return
        
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Define column order matching existing format
        columns = [
            "title", "url", "source_date", "incident_type", "date", 
            "location", "victim_identity", "description", "severity", 
            "perpetrator_info", "latitude", "longitude"
        ]
        
        # Load existing data if file exists
        if OUTPUT_CSV.exists():
            try:
                df_existing = pd.read_csv(OUTPUT_CSV)
                # Ensure all columns exist
                for col in columns:
                    if col not in df_existing.columns:
                        df_existing[col] = None
                df_existing = df_existing[columns]  # Reorder columns
                logger.info(f"Loaded {len(df_existing)} existing incidents from {OUTPUT_CSV}")
            except Exception as e:
                logger.warning(f"Error loading existing CSV: {e}. Starting fresh.")
                df_existing = pd.DataFrame(columns=columns)
        else:
            df_existing = pd.DataFrame(columns=columns)
            logger.info(f"Creating new CSV file: {OUTPUT_CSV}")
        
        # Create DataFrame from new rows, ensuring all columns exist
        df_new = pd.DataFrame(new_rows)
        for col in columns:
            if col not in df_new.columns:
                df_new[col] = None
        df_new = df_new[columns]  # Reorder columns
        
        # Combine with existing
        if len(df_existing) > 0:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Save to CSV
        df_combined.to_csv(OUTPUT_CSV, index=False)
        
        logger.info(f"Saved {len(new_rows)} new incidents to {OUTPUT_CSV}")
        logger.info(f"Total incidents in file: {len(df_combined)}")
    
    def _commit_changes(self):
        """Commit changes to git."""
        try:
            # Check if git is available
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.warning("Git not available. Skipping commit.")
                return
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Git not found. Skipping commit.")
            return
        
        # Check if there are changes
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", str(OUTPUT_CSV)],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(BASE_DIR)
            )
            
            if not result.stdout.strip():
                logger.info("No changes to commit.")
                return
            
            # Configure git user (if not already configured)
            subprocess.run(
                ["git", "config", "user.email", "action@github.com"],
                capture_output=True,
                timeout=5,
                cwd=str(BASE_DIR)
            )
            subprocess.run(
                ["git", "config", "user.name", "GitHub Action"],
                capture_output=True,
                timeout=5,
                cwd=str(BASE_DIR)
            )
            
            # Add changes
            subprocess.run(
                ["git", "add", str(OUTPUT_CSV)],
                check=True,
                capture_output=True,
                timeout=5,
                cwd=str(BASE_DIR)
            )
            
            # Commit
            commit_message = (
                f"Daily RSS Monitor: Add {self.stats['unique_new']} new incidents "
                f"({datetime.now().strftime('%Y-%m-%d')})"
            )
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                capture_output=True,
                timeout=5,
                cwd=str(BASE_DIR)
            )
            
            # Push
            subprocess.run(
                ["git", "push"],
                check=True,
                capture_output=True,
                timeout=30,
                cwd=str(BASE_DIR)
            )
            
            logger.info(f"Successfully committed and pushed {self.stats['unique_new']} new incidents")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
        except Exception as e:
            logger.error(f"Error during git commit: {e}")
    
    def _print_summary(self):
        """Print final summary statistics."""
        logger.info("\n" + "=" * 70)
        logger.info("RSS MONITOR - Complete")
        logger.info("=" * 70)
        logger.info(f"Feeds processed: {self.stats['feeds_processed']}")
        logger.info(f"Articles fetched: {self.stats['articles_fetched']}")
        logger.info(f"Incidents extracted: {self.stats['incidents_extracted']}")
        logger.info(f"Geocoded: {self.stats['geocoded']}")
        logger.info(f"Unique new incidents: {self.stats['unique_new']}")
        logger.info(f"Duplicates found: {self.stats['duplicates_found']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Duration: {self.stats.get('duration_seconds', 0):.1f} seconds")
        logger.info("=" * 70)


def main():
    """Main entry point for the script."""
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
        help="Run without saving files or committing (for testing)"
    )
    
    args = parser.parse_args()
    
    try:
        monitor = RSSMonitorScript(
            hours_back=args.hours_back,
            dry_run=args.dry_run
        )
        exit_code = monitor.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

