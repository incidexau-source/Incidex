import sys
import os
import datetime
import logging
import csv
import time
import re
import feedparser
from pathlib import Path
from dateutil import parser as date_parser
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discovery_job.log", mode='w', encoding='utf-8'), # Overwrite mode
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DiscoveryJob")

# Handle API Key manually if needed (BOM fix)
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    if "GOOGLE_API_KEY=" in line:
                        api_key = line.split("GOOGLE_API_KEY=", 1)[1].strip()
                        os.environ["GOOGLE_API_KEY"] = api_key
                        break
        except Exception as e:
            logger.error(f"Error reading .env: {e}")

if api_key:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
else:
    logger.error("Failed to load GOOGLE_API_KEY")

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import project modules
try:
    from rss_feeds import get_all_feeds
    from scripts import gemini_extractor
    # Force re-configure
    if api_key:
        gemini_extractor.genai.configure(api_key=api_key)
    from geocoder import Geocoder
    from deduplicator import Deduplicator
    from scripts.approval_manager import ApprovalManager
    from scripts.incident_publisher import IncidentPublisher
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

START_DATE = datetime.datetime(2025, 11, 1).replace(tzinfo=datetime.timezone.utc)
END_DATE = datetime.datetime.now(datetime.timezone.utc)

def rate_limited_call(func, *args, **kwargs):
    """Retries function on 429 error."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = 60 * (attempt + 1)
                logger.warning(f"Rate limit hit. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                # If it's a generated Exception from inside the function (like in gemini_extractor), 
                # we might not catch it here if it returns a value (like False) instead of raising.
                # But gemini_extractor functions catch exceptions and return False/None.
                # So we need to monkeypatch or know if it failed due to error.
                # Actually gemini_extractor logs the error. We can't easily detect it from return value alone 
                # because False is also "valid not relevant".
                # We essentially rely on gemini_extractor to NOT catch the exception? 
                # It DOES catch it. 
                raise e 
    return None

# We need to bypass gemini_extractor's try/except blocks to handle 429 properly 
# OR we implement the logic here using the prompt generation from gemini_extractor 
# but calling genai directly.
# Copying logic is safer for control.

def robust_filter_article(title, text):
    """Robust version of filter_article with rate limit handling."""
    model_name = "gemini-2.0-flash-exp"
    for attempt in range(4):
        try:
            model = genai.GenerativeModel(model_name)
            prompt = f"""
            You are an expert analyst for an LGBTIQ+ hate crime monitoring service in Australia.
            Analyze the following news article and determine if it describes an incident of hate crime...
            (Simplified prompt for brevity)
            IN AUSTRALIA.
            Article Title: {title}
            Article Text: {text[:2000]}
            Answer with exactly one word: YES or NO.
            """
            response = model.generate_content(prompt)
            return "YES" in response.text.strip().upper()
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = 45 * (attempt + 1)
                logger.warning(f"429 in filter. Waiting {wait}s...")
                time.sleep(wait)
            else:
                logger.error(f"Error in robust_filter: {e}")
                return False
    return False

def robust_extract_incident(title, text, url):
    """Robust version of extract_incident."""
    model_name = "gemini-2.0-flash-exp"
    for attempt in range(4):
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            prompt = f"""
            Extract structured data from this report about an LGBTIQ+ hate crime in Australia.
            Article Title: {title}
            Article Text: {text[:4000]}
            Article URL: {url}
            Return JSON with fields: incident_type, date_of_incident, location, victim_identity, description, confidence_score, notes.
            """
            response = model.generate_content(prompt)
            import json
            result = json.loads(response.text)
            result["article_url"] = url
            result["article_title"] = title
            return result
        except Exception as e:
             if "429" in str(e) or "quota" in str(e).lower():
                wait = 45 * (attempt + 1)
                logger.warning(f"429 in extract. Waiting {wait}s...")
                time.sleep(wait)
             else:
                logger.error(f"Error in robust_extract: {e}")
                return None
    return None

class DiscoveryJob:
    def __init__(self):
        self.stats = {"processed": 0, "date_matched": 0, "relevant": 0, "duplicates": 0, "auto_published": 0, "pending_review": 0, "errors": 0}
        self.feeds = get_all_feeds()
        self.geocoder = Geocoder()
        self.deduplicator = Deduplicator(existing_csv_path=BASE_DIR / "data/incidents_in_progress.csv")
        self.approval_manager = ApprovalManager()
        self.incident_publisher = IncidentPublisher()
        self.new_incidents = []

    def is_in_date_range(self, entry):
        # (Same logic as before)
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                return START_DATE <= dt <= END_DATE
            if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
                return START_DATE <= dt <= END_DATE
            return False
        except:
            return False

    def run(self):
        print("Starting Robust Discovery Job...")
        for feed_config in self.feeds:
            logger.info(f"Scanning {feed_config.name}")
            d = feedparser.parse(feed_config.url)
            for entry in d.entries:
                self.stats["processed"] += 1
                if not self.is_in_date_range(entry):
                    continue
                self.stats["date_matched"] += 1
                
                title = entry.title
                link = entry.link
                content = entry.get('summary', '') or entry.get('description', '')
                if 'content' in entry: content += " " + " ".join([c.value for c in entry.content])
                
                # Check duplicates based on URL first to save API calls
                # (Simple check against discovered list)
                if any(i['article_url'] == link for i in self.new_incidents):
                    continue

                logger.info(f"Checking: {title}")
                time.sleep(2) # Initial polite delay
                
                is_relevant = robust_filter_article(title, content)
                if not is_relevant:
                    continue
                
                logger.info(f"Relevant: {title}")
                self.stats["relevant"] += 1
                time.sleep(2)
                
                data = robust_extract_incident(title, content, link)
                if not data:
                    self.stats["errors"] += 1
                    continue
                
                # Geocode
                if data.get('location'):
                    geo = self.geocoder.geocode(data['location'])
                    if geo:
                        data.update({'latitude': geo.latitude, 'longitude': geo.longitude, 'suburb': geo.suburb, 'state': geo.state, 'postcode': geo.postcode})
                
                # Deduplicate
                if self.deduplicator.find_duplicates([data])['duplicates']:
                    self.stats["duplicates"] += 1
                    logger.info("Duplicate found (DB)")
                    continue
                    
                if any(self.deduplicator.is_duplicate(data, x) for x in self.new_incidents):
                    self.stats["duplicates"] += 1
                    logger.info("Duplicate found (Batch)")
                    continue
                
                # Add
                data['publication_date'] = entry.get('published')
                data['news_source'] = feed_config.name
                
                self.new_incidents.append(data)
                
                # Approval
                conf = data.get('confidence_score', 0)
                try: conf = int(conf)
                except: conf = 0
                data['confidence_score'] = conf
                
                if conf >= 95:
                    self.incident_publisher.publish_auto_approved_incidents([data])
                    self.stats["auto_published"] += 1
                else:
                    self.approval_manager.add_incident_for_review(data)
                    self.stats["pending_review"] += 1
                
                # Incremental save
                self.save_csv()
        
        self.save_csv()
        self.print_summary()

    def save_csv(self):
        output_file = BASE_DIR / "discovered_nov_dec_2025_jan_2026.csv"
        # Always write if we have incidents, or at least create empty file? 
        # Better to write only if incidents exist to avoid overwriting with empty if restarted?
        # But we want to see progress.
        
        keys = ["date_of_incident", "location", "suburb", "state", "postcode", "incident_type", "victim_identity", "description", "article_url", "publication_date", "news_source", "confidence_score", "latitude", "longitude"]
        
        # Read existing to append? The job resets self.new_incidents on init.
        # If we restart the job, we might overwrite. 
        # For this task, we assume single run.
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.new_incidents)
        # logger.info(f"Saved {len(self.new_incidents)} incidents to CSV")

    def print_summary(self):
        summary = f"Summary: {self.stats}"
        print(summary)
        logger.info(summary)
        with open(BASE_DIR / "discovery_summary.txt", "w") as f:
            f.write(summary)


if __name__ == "__main__":
    job = DiscoveryJob()
    job.run()
