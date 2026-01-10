"""
RSS Agent for Incidex
Autonomous daily RSS monitoring agent.
"""

import os
import sys
import datetime
import logging
import feedparser
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Set, Any
from dotenv import load_dotenv

# Import local modules
# Add parent directory to path to allow imports if running from scripts/
sys.path.append(str(Path(__file__).parent.parent))

from rss_feeds import get_all_feeds
from scripts import gemini_extractor
from geocoder import Geocoder
from deduplicator import Deduplicator
from scripts.approval_manager import ApprovalManager
from scripts.incident_publisher import IncidentPublisher
from scripts.email_handler import EmailHandler
from article_fetcher import ArticleFetcher, ArticleData

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rss_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RSSAgent")

PROCESSED_URLS_FILE = Path("data/processed_urls.txt")
INCIDENTS_FILE = Path("data/incidents_news_sourced.csv")
REVIEW_DIR = Path("data/review")
REPORT_FILE = Path("daily_report.txt")

# Keywords to trigger deep fetching
FETCH_KEYWORDS = [
    'assault', 'attack', 'murder', 'police', 'court', 'crime', 'violent', 'violence',
    'abuse', 'harass', 'discriminat', 'hate', 'gay', 'trans', 'lgbt', 'queer', 
    'homophob', 'transphob', 'conversion', 'bashing', 'kill', 'stab', 'punch', 
    'offender', 'victim', 'sentenced', 'charged', 'arrested'
]


class RSSAgent:
    def __init__(self):
        self.feeds = get_all_feeds()
        self.processed_urls = self._load_processed_urls()
        self.geocoder = Geocoder()
        self.deduplicator = Deduplicator(existing_csv_path="data/incidents_in_progress.csv")
        self.approval_manager = ApprovalManager()
        self.incident_publisher = IncidentPublisher()
        self.email_handler = EmailHandler()
        self.article_fetcher = ArticleFetcher()
        self.new_incidents: List[Dict] = []
        self.auto_publish_incidents: List[Dict] = []
        self.pending_review_incidents: List[Dict] = []
        self.stats = {
            "processed_articles": 0,
            "relevant_found": 0,
            "duplicates_blocked": 0,
            "pending_review": 0,
            "auto_published": 0
        }
        
    def _load_processed_urls(self) -> Set[str]:
        if PROCESSED_URLS_FILE.exists():
            with open(PROCESSED_URLS_FILE, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f)
        return set()

    def _save_processed_url(self, url: str):
        with open(PROCESSED_URLS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{url}\n")
        self.processed_urls.add(url)

    def run(self):
        logger.info("Starting RSS Agent run...")
        
        for feed_config in self.feeds:
            logger.info(f"Checking feed: {feed_config.name}")
            try:
                feed = feedparser.parse(feed_config.url)
                
                for entry in feed.entries:
                    url = entry.link
                    title = entry.title
                    # Some feeds put content in 'summary' or 'content'
                    content = entry.get('summary', '') or entry.get('description', '') 
                    if 'content' in entry:
                         content += " " + " ".join([c.value for c in entry.content])

                    if url in self.processed_urls:
                        continue
                    
                    self.stats["processed_articles"] += 1
                    
                    # Check if we should fetch full text
                    # Logic: If content is short AND contains relevant keywords, fetch full text
                    if len(content) < 800:
                        combined_text = (title + " " + content).lower()
                        if any(kw in combined_text for kw in FETCH_KEYWORDS):
                            logger.info(f"Fetching full text for potential match: {title}")
                            try:
                                article_data = ArticleData(
                                    title=title,
                                    url=url,
                                    publication_date=datetime.datetime.now(),
                                    summary=content
                                )
                                self.article_fetcher.extract_article_text(article_data)
                                if article_data.full_text:
                                    content = article_data.full_text
                                    logger.info(f"Updated content length: {len(content)}")
                            except Exception as e:
                                logger.warning(f"Failed to fetch {url}: {e}")

                    # Step 1: Filter (Is it LGBTIQ+ hate crime?)
                    is_relevant = gemini_extractor.filter_article(title, content)
                    
                    if not is_relevant:
                        self._save_processed_url(url) # Mark as processed so we don't check again
                        continue
                        
                    logger.info(f"Found relevant article: {title}")
                    self.stats["relevant_found"] += 1
                    
                    # Step 2: Extract Structured Data
                    incident_data = gemini_extractor.extract_incident(title, content, url)
                    
                    if not incident_data:
                        logger.error(f"Failed to extract data for {url}")
                        continue
                    
                    # Step 3: Geocode
                    location_str = incident_data.get("location")
                    if location_str:
                        geo_result = self.geocoder.geocode(location_str)
                        if geo_result:
                            incident_data["latitude"] = geo_result.latitude
                            incident_data["longitude"] = geo_result.longitude
                            incident_data["suburb"] = geo_result.suburb
                            incident_data["state"] = geo_result.state
                            incident_data["postcode"] = geo_result.postcode
                    
                    # Step 4: Deduplicate
                    # We create a temporary list with just this incident to check against DB
                    # The deduplicator requires a list of dicts
                    dedup_result = self.deduplicator.find_duplicates([incident_data])
                    
                    # If it's a duplicate of an EXISTING incident, we drop it
                    if dedup_result["duplicates"] and dedup_result["duplicates"][0]["match_type"] == "existing":
                        logger.info(f"Duplicate found for {url} - skipping.")
                        self.stats["duplicates_blocked"] += 1
                        self._save_processed_url(url)
                        continue
                        
                    # If it's unique or only duplicates other NEW incidents (which shouldn't happen in this loop logic often unless feed has duplicates), we proceed.
                    # Actually, if we process one by one, 'dedup against new' isn't checking against the batch we are building *in this run* yet unless we pass self.new_incidents to find_duplicates each time.
                    # Better optimization: Collect all relevant incidents first, then dedup batch? 
                    # For now, let's just check against DB. We can check against `self.new_incidents` manually.
                    
                    is_batch_duplicate = False
                    for existing_new in self.new_incidents:
                        if self.deduplicator.is_duplicate(incident_data, existing_new):
                            is_batch_duplicate = True
                            break
                    
                    if is_batch_duplicate:
                        logger.info(f"Duplicate found in current batch for {url} - skipping.")
                        self.stats["duplicates_blocked"] += 1
                        self._save_processed_url(url)
                        continue

                    # Step 5: Validate and Route to Approval Workflow
                    # Check confidence
                    confidence = incident_data.get("confidence_score", 0)
                    if isinstance(confidence, str):
                        try:
                            confidence = int(confidence)
                        except:
                            confidence = 0
                            
                    incident_data["confidence_score"] = confidence
                    incident_data["source_feed"] = feed_config.name
                    incident_data["date_scraped"] = datetime.datetime.now().isoformat()
                    
                    # Route based on confidence threshold (95% for auto-publish)
                    if confidence >= 95:
                        # Auto-publish (high confidence)
                        self.auto_publish_incidents.append(incident_data)
                        self.stats["auto_published"] += 1
                        logger.info(f"Auto-publish incident (confidence {confidence}%): {title}")
                    else:
                        # Needs human approval (confidence < 95%)
                        incident_id = self.approval_manager.add_incident_for_review(incident_data)
                        self.pending_review_incidents.append(incident_data)
                        self.stats["pending_review"] += 1
                        logger.info(f"Incident pending review (confidence {confidence}%): {title} [ID: {incident_id}]")
                    
                    self._save_processed_url(url)
            
            except Exception as e:
                logger.error(f"Error processing feed {feed_config.name}: {e}")

        # Process auto-published incidents
        if self.auto_publish_incidents:
            logger.info(f"Publishing {len(self.auto_publish_incidents)} auto-approved incidents...")
            publish_stats = self.incident_publisher.publish_auto_approved_incidents(self.auto_publish_incidents)
            logger.info(f"Auto-published {publish_stats['published_count']} incidents")
        
        # Send daily summary email
        try:
            logger.info("Sending daily summary email...")
            self.email_handler.send_auto_published_summary(
                self.auto_publish_incidents,
                self.approval_manager.get_pending_incidents()
            )
            logger.info("Daily summary email sent")
        except Exception as e:
            logger.error(f"Error sending daily summary email: {e}")
        
        # Generate Report
        self._generate_report()
        logger.info("RSS Agent run complete.")

            
    def _generate_report(self):
        pending_count = len(self.approval_manager.get_pending_incidents())
        report = f"""Incidex Daily Scrape Report [{datetime.date.today()}]
        
Processed Articles: {self.stats['processed_articles']}
Relevant Incidents Found: {self.stats['relevant_found']}
Duplicates Blocked: {self.stats['duplicates_blocked']}
Auto-Published (confidence ≥95%): {self.stats['auto_published']}
Pending Review (confidence <95%): {self.stats['pending_review']}
Total Pending in Queue: {pending_count}

Workflow Status:
- Auto-published incidents have been added to the main database
- Pending incidents require human approval via email

Estimated Cost: $0.00 (Free Tier)
"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
            
if __name__ == "__main__":
    agent = RSSAgent()
    agent.run()
