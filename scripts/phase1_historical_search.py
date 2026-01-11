
import os
import sys
import csv
import time
import json
import requests
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from scripts.config import GOOGLE_API_KEY, PHASE1_OUTPUT, START_YEAR, END_YEAR
from scripts.gemini_extractor import robust_filter_article, robust_extract_incident
from article_fetcher import ArticleFetcher

# Files for persistence
PROGRESS_LOG = os.path.join(os.path.dirname(PHASE1_OUTPUT), "phase1_progress.json")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("phase1_search.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Phase1")

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

LGBTIQ_DOMAINS = ["starobserver.com.au", "pinknewsaustralia.com", "staunch.org.au", "prideinpractice.org.au", "lgbtiqlegalaustraliainfo.org.au"]
MAINSTREAM_DOMAINS = ["abc.net.au", "theguardian.com", "sbs.com.au", "smh.com.au", "theage.com.au"]

def search_gdelt(query: str, start_year: int, end_year: int, max_records: int = 150):
    actual_start = max(start_year, 2017)
    if actual_start > end_year: return []
    
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "sort": "DateDesc",
        "startdatetime": f"{actual_start}0101000000",
        "enddatetime": f"{end_year}1231235959"
    }
    
    try:
        resp = requests.get(GDELT_URL, params=params, timeout=30)
        if resp.status_code == 200:
            if "Your query was too short or too long" in resp.text:
                return []
            data = resp.json()
            return data.get("articles", [])
        elif resp.status_code == 429:
            time.sleep(5)
    except: pass
    return []

def load_progress():
    if os.path.exists(PROGRESS_LOG):
        try:
            with open(PROGRESS_LOG, 'r') as f:
                return set(json.load(f))
        except: pass
    return set()

def save_progress(processed_urls):
    with open(PROGRESS_LOG, 'w') as f:
        json.dump(list(processed_urls), f)

def run_phase1():
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY missing.")
        return

    fetcher = ArticleFetcher()
    processed_urls = load_progress()
    seen_urls = set()
    all_candidates = []

    logger.info("Starting Phase 1: Robust Discovery (2017-2025)")

    # 1. Harvest from LGBTIQ Sources
    for domain in LGBTIQ_DOMAINS:
        logger.info(f"Mining LGBTIQ source: {domain}")
        query = f'domain:{domain} (assault OR violence OR "hate crime" OR bashing OR attack OR harassment OR discrimination)'
        results = search_gdelt(query, START_YEAR, END_YEAR)
        for art in results:
            url = art.get('url')
            if url and url not in seen_urls:
                all_candidates.append({**art, "source_domain": domain})
                seen_urls.add(url)
    
    # 2. Harvest from Mainstream (Targeted)
    for domain in MAINSTREAM_DOMAINS:
        logger.info(f"Mining Mainstream: {domain}")
        # One powerful combined query per mainstream domain
        # Using broad markers to capture as much as possible
        query = f'domain:{domain} (assault OR violence OR "hate crime" OR murder OR bashing OR attack) (LGBTIQ OR gay OR lesbian OR transgender OR homophobic OR transphobic OR queer)'
        results = search_gdelt(query, START_YEAR, END_YEAR, max_records=250)
        for art in results:
            url = art.get('url')
            if url and url not in seen_urls:
                all_candidates.append({**art, "source_domain": domain})
                seen_urls.add(url)
        time.sleep(1)

    new_articles = [a for a in all_candidates if a['url'] not in processed_urls]
    logger.info(f"Harvested {len(all_candidates)} candidates. {len(new_articles)} are new.")

    fieldnames = [
        "date_of_incident", "location", "incident_type", "victim_identity", 
        "description", "confidence_score", "severity", "article_url", 
        "article_title", "source_name", "publication_date", "discovery_date"
    ]

    if not os.path.exists(PHASE1_OUTPUT):
        pd.DataFrame(columns=fieldnames).to_csv(PHASE1_OUTPUT, index=False)

    found_count = 0
    for idx, art in enumerate(new_articles):
        title = art.get('title', 'Unknown')
        url = art.get('url')
        snippet = art.get('snippet', '')
        
        logger.info(f"[{idx+1}/{len(new_articles)}] Analyzing: {title[:70]}")
        
        # Use snippet primary, fetch if necessary
        context_text = snippet
        if not snippet or len(snippet) < 150:
            try:
                from article_fetcher import ArticleData
                temp_art = ArticleData(title=title, url=url, publication_date=datetime.now())
                temp_art = fetcher.extract_article_text(temp_art)
                if temp_art.full_text:
                    context_text = temp_art.full_text[:3000]
            except: pass

        if not context_text: continue # Skip if no text at all

        try:
            if robust_filter_article(title, context_text):
                incident = robust_extract_incident(title, context_text, url)
                if incident and incident.get('confidence_score', 0) >= 65:
                    incident.update({
                        "source_name": art.get('source_domain', 'Unknown'),
                        "publication_date": art.get('seendate', ""),
                        "discovery_date": datetime.now().isoformat(),
                        "article_url": url,
                        "article_title": title
                    })
                    row = pd.DataFrame([{k: incident.get(k, "") for k in fieldnames}])
                    row.to_csv(PHASE1_OUTPUT, mode='a', header=False, index=False)
                    found_count += 1
                    logger.info(f"  -> SUCCESS! Found {incident['incident_type']} in {incident['location']}")
            
            processed_urls.add(url)
            if (idx + 1) % 5 == 0: save_progress(processed_urls)
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")

    save_progress(processed_urls)
    logger.info(f"Phase 1 complete. Found {found_count} new incidents.")

if __name__ == "__main__":
    run_phase1()
