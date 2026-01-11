
import os
import sys
import datetime
import logging
import csv
import time
import feedparser
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from scripts.config import GOOGLE_API_KEY
from scripts.gemini_extractor import robust_filter_article, robust_extract_incident
from geocoder import Geocoder
from deduplicator import Deduplicator
from scripts.approval_manager import ApprovalManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discovery_job.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscoveryJob")

# Configurable Range
START_DATE = datetime.datetime(2025, 11, 1).replace(tzinfo=datetime.timezone.utc)
END_DATE = datetime.datetime.now(datetime.timezone.utc)

class DiscoveryJob:
    def __init__(self):
        self.stats = {
            "processed": 0, 
            "date_matched": 0, 
            "relevant": 0, 
            "duplicates": 0, 
            "saved": 0,
            "errors": 0
        }
        try:
            from rss_feeds import get_all_feeds
            self.feeds = get_all_feeds()
        except:
            logger.error("Could not load rss_feeds.py")
            self.feeds = []
            
        self.geocoder = Geocoder()
        self.deduplicator = Deduplicator(existing_csv_path=BASE_DIR / "data/incidents_in_progress.csv")
        self.approval_manager = ApprovalManager()
        self.new_incidents = []

    def is_in_date_range(self, entry):
        for attr in ['published_parsed', 'updated_parsed']:
            if hasattr(entry, attr) and getattr(entry, attr):
                try:
                    dt = datetime.datetime(*getattr(entry, attr)[:6], tzinfo=datetime.timezone.utc)
                    return START_DATE <= dt <= END_DATE
                except: continue
        return False

    def run(self):
        logger.info(f"Starting Discovery Job for range: {START_DATE.date()} to {END_DATE.date()}")
        
        for feed in self.feeds:
            logger.info(f"Scanning Feed: {feed.name}")
            try:
                parsed = feedparser.parse(feed.url)
                for entry in parsed.entries:
                    self.stats["processed"] += 1
                    if not self.is_in_date_range(entry):
                        continue
                    self.stats["date_matched"] += 1
                    
                    title = entry.title
                    url = entry.link
                    content = entry.get('summary', '') or entry.get('description', '')
                    
                    # Filtering
                    if robust_filter_article(title, content):
                        logger.info(f"  RELEVANT: {title[:60]}")
                        self.stats["relevant"] += 1
                        
                        # Extraction
                        incident = robust_extract_incident(title, content, url)
                        if incident and incident.get('confidence_score', 0) >= 65:
                            # Geocoding
                            loc = incident.get('location')
                            if loc:
                                geo = self.geocoder.geocode(loc)
                                if geo:
                                    incident.update({
                                        'lat': geo.latitude,
                                        'lng': geo.longitude,
                                        'suburb': geo.suburb,
                                        'state': geo.state
                                    })
                            
                            # Deduplication
                            is_dup = self.deduplicator.is_duplicate(incident, {}) # Check internal logic would be better
                            # For simplicity in this script, we check against newly found in this run
                            if any(self.deduplicator.is_duplicate(incident, x) for x in self.new_incidents):
                                self.stats["duplicates"] += 1
                                continue
                                
                            incident['news_source'] = feed.name
                            incident['discovery_date'] = datetime.datetime.now().isoformat()
                            
                            # Add to Review Queue
                            self.approval_manager.add_incident_for_review(incident)
                            self.new_incidents.append(incident)
                            self.stats["saved"] += 1
                            logger.info(f"    -> SAVED TO QUEUE: {incident['incident_type']}")
                            
                            self.save_progress()
            except Exception as e:
                logger.error(f"Error scanning feed {feed.name}: {e}")

        self.print_summary()

    def save_progress(self):
        output_file = BASE_DIR / "data" / "discovery_results_recent.csv"
        os.makedirs(output_file.parent, exist_ok=True)
        pd.DataFrame(self.new_incidents).to_csv(output_file, index=False)

    def print_summary(self):
        summary = f"\nDiscovery Summary:\n{json.dumps(self.stats, indent=2)}"
        print(summary)
        with open(BASE_DIR / "data" / "discovery_summary.txt", "w") as f:
            f.write(summary)

if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
    else:
        job = DiscoveryJob()
        job.run()
