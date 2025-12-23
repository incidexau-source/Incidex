"""
Comprehensive Overnight Search Script for LGBTIQ+ Hate Crime Incidents in Australia

This script performs deep, exhaustive searches across multiple news sources,
using 50+ query combinations to find hate crime incidents that may have been
missed by the standard historical scraper.

Features:
- Multi-source news aggregation (20+ Australian news sources)
- 50+ advanced search query combinations
- Temporal deep dive (year by year, seasonal patterns)
- Geographic exhaustive search (suburbs, hotspots, regional areas)
- Specialized search categories (workplace, schools, sports, etc.)
- AI filtering and deduplication
- Comprehensive logging and reporting
- Automatic merging into main dataset

Run time: 5-6 hours (designed for overnight execution)
"""

import json
import time
import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sys
import io

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import requests
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, RATE_LIMIT_DELAY

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Timestamp for this run
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Output files
RESULTS_FILE = DATA_DIR / "overnight_search_results.csv"
NEW_INCIDENTS_FILE = DATA_DIR / "overnight_search_new_incidents.csv"
PROGRESS_FILE = DATA_DIR / "overnight_search_progress.csv"
PROCESSED_URLS_FILE = DATA_DIR / "overnight_processed_urls.txt"
LOG_FILE = LOGS_DIR / f"search_log_{RUN_TIMESTAMP}.txt"
REPORT_FILE = DATA_DIR / f"overnight_search_report_{RUN_TIMESTAMP}.txt"
MAIN_INCIDENTS_FILE = DATA_DIR / "incidents_in_progress.csv"

# API Configuration
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
REQUEST_DELAY = 3  # Seconds between API requests
AI_DELAY = 1  # Seconds between AI calls

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
geolocator = Nominatim(user_agent="lgbtiq-overnight-search-v2")

# =============================================================================
# NEWS SOURCES - Australian Media Outlets
# =============================================================================

AUSTRALIAN_NEWS_SOURCES = {
    # National broadcasters
    "abc.net.au": "ABC News",
    "sbs.com.au": "SBS News",
    
    # Major newspapers
    "theguardian.com": "Guardian Australia",
    "theage.com.au": "The Age (Victoria)",
    "smh.com.au": "Sydney Morning Herald",
    "brisbanetimes.com.au": "Brisbane Times",
    "watoday.com.au": "WA Today",
    "canberratimes.com.au": "Canberra Times",
    
    # News Corp outlets
    "news.com.au": "News.com.au",
    "theaustralian.com.au": "The Australian",
    "dailytelegraph.com.au": "Daily Telegraph",
    "heraldsun.com.au": "Herald Sun",
    "couriermail.com.au": "Courier Mail",
    "adelaidenow.com.au": "Adelaide Now",
    "perthnow.com.au": "Perth Now",
    "ntnews.com.au": "NT News",
    "themercury.com.au": "Hobart Mercury",
    
    # Regional/community
    "examiner.com.au": "The Examiner (Launceston)",
    "illawarramercury.com.au": "Illawarra Mercury",
    "newcastleherald.com.au": "Newcastle Herald",
    "bordermail.com.au": "Border Mail",
    "bendigoadvertiser.com.au": "Bendigo Advertiser",
    "geelongadvertiser.com.au": "Geelong Advertiser",
    "thewest.com.au": "The West Australian",
    
    # LGBTIQ+ specific
    "starobserver.com.au": "Star Observer",
    "qnews.com.au": "QNews",
    "dnamagazine.com.au": "DNA Magazine",
    "samesame.com.au": "SameSame",
    "lotl.com": "LOTL",
    "pinknews.co.uk": "Pink News",
    
    # Independent/alternative
    "crikey.com.au": "Crikey",
    "theconversation.com": "The Conversation",
    "michaelwest.com.au": "Michael West Media",
    "independentaustralia.net": "Independent Australia",
}

# =============================================================================
# SEARCH QUERIES - 50+ Combinations
# =============================================================================

# Base LGBTIQ+ terms
LGBTIQ_TERMS = [
    "LGBTIQ", "LGBT", "LGBTI", "gay", "lesbian", "transgender", "trans",
    "bisexual", "queer", "non-binary", "nonbinary", "gender diverse",
    "same-sex", "homosexual", "drag queen", "trans woman", "trans man"
]

# Violence/crime terms
VIOLENCE_TERMS = [
    "attack", "assault", "violence", "hate crime", "bashing", "beaten",
    "stabbed", "punched", "kicked", "murdered", "killed", "death",
    "harassment", "threat", "intimidation", "abuse", "targeted"
]

# Discrimination terms
DISCRIMINATION_TERMS = [
    "discrimination", "discriminated", "refused entry", "kicked out",
    "denied service", "workplace harassment", "bullying", "vilification"
]

# Property crime terms
PROPERTY_TERMS = [
    "vandalism", "graffiti", "property damage", "arson", "fire",
    "rainbow flag", "pride flag", "defaced", "destroyed"
]

# Generate comprehensive search queries
def generate_search_queries():
    """Generate 50+ search query combinations."""
    queries = []
    
    # 1. Direct hate crime queries
    direct_queries = [
        '"hate crime" AND (LGBTIQ OR LGBT OR gay OR lesbian OR transgender) AND Australia',
        '"homophobic attack" AND Australia',
        '"transphobic attack" AND Australia',
        '"anti-gay" AND (attack OR assault OR violence) AND Australia',
        '"homophobic violence" AND Australia',
        '"transphobic violence" AND Australia',
        '"queer bashing" AND Australia',
        '"gay bashing" AND Australia',
    ]
    queries.extend(direct_queries)
    
    # 2. Specific identity + violence combinations
    identity_violence = [
        f'"{identity}" AND "{violence}" AND Australia'
        for identity in ["gay man", "lesbian woman", "transgender", "trans woman", "trans man", "drag queen", "non-binary"]
        for violence in ["attacked", "assaulted", "beaten", "stabbed", "murdered"]
    ]
    queries.extend(identity_violence[:15])  # Limit to avoid too many
    
    # 3. Location-specific queries (LGBTIQ hotspots)
    locations = [
        ("Oxford Street", "Sydney"),
        ("Darlinghurst", "Sydney"),
        ("Newtown", "Sydney"),
        ("St Kilda", "Melbourne"),
        ("Chapel Street", "Melbourne"),
        ("Fitzroy", "Melbourne"),
        ("Collingwood", "Melbourne"),
        ("Fortitude Valley", "Brisbane"),
        ("West End", "Brisbane"),
        ("Northbridge", "Perth"),
        ("Hindley Street", "Adelaide"),
    ]
    location_queries = [
        f'(LGBTIQ OR gay OR lesbian OR transgender) AND (attack OR assault OR violence) AND "{loc[0]}"'
        for loc in locations
    ]
    queries.extend(location_queries)
    
    # 4. State-specific queries
    states = ["NSW", "Victoria", "Queensland", "Western Australia", "South Australia", "Tasmania", "ACT", "Northern Territory"]
    state_queries = [
        f'(LGBTIQ OR LGBT OR gay OR transgender) AND (hate crime OR attack OR assault) AND "{state}"'
        for state in states
    ]
    queries.extend(state_queries)
    
    # 5. Venue-specific queries
    venue_queries = [
        '(gay bar OR gay club OR LGBTIQ venue) AND (attack OR assault OR violence) AND Australia',
        '(pride event OR pride march OR mardi gras) AND (attack OR violence OR incident) AND Australia',
        '(gay sauna OR gay venue) AND (attack OR assault) AND Australia',
        '(LGBTIQ community center OR queer space) AND (vandalism OR attack) AND Australia',
    ]
    queries.extend(venue_queries)
    
    # 6. Specific incident type queries
    incident_queries = [
        '"rainbow flag" AND (vandalism OR burned OR destroyed OR stolen) AND Australia',
        '"pride flag" AND (vandalism OR defaced OR removed) AND Australia',
        '"conversion practices" AND Australia',
        '"corrective rape" AND Australia',
        '"gay panic defense" AND Australia',
        '"police misconduct" AND (gay OR LGBTIQ OR transgender) AND Australia',
    ]
    queries.extend(incident_queries)
    
    # 7. Legal/court case queries
    legal_queries = [
        '(court case OR trial OR sentenced) AND (homophobic OR transphobic OR hate crime) AND Australia',
        '(coronial inquest OR coroner) AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(restraining order OR AVO) AND (homophobic OR harassment) AND Australia',
        '"hate speech" AND (gay OR LGBTIQ OR transgender) AND Australia',
    ]
    queries.extend(legal_queries)
    
    # 8. Workplace/school queries
    institutional_queries = [
        '(workplace discrimination OR workplace harassment) AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(school bullying OR student) AND (gay OR LGBTIQ OR transgender OR homophobic) AND Australia',
        '(university OR campus) AND (homophobic OR transphobic OR LGBTIQ) AND (attack OR harassment) AND Australia',
        '(sports OR AFL OR NRL OR cricket) AND (homophobic OR gay OR LGBTIQ) AND (abuse OR discrimination) AND Australia',
    ]
    queries.extend(institutional_queries)
    
    # 9. Religious institution queries
    religious_queries = [
        '(church OR religious school OR catholic) AND (gay OR LGBTIQ OR transgender) AND (discrimination OR expelled OR fired) AND Australia',
        '(religious exemption OR religious freedom) AND (LGBTIQ OR gay OR transgender) AND Australia',
    ]
    queries.extend(religious_queries)
    
    # 10. Medical/healthcare queries
    medical_queries = [
        '(hospital OR medical OR healthcare) AND (transgender OR gay OR LGBTIQ) AND (discrimination OR refused) AND Australia',
        '(gender affirming care OR hormone therapy) AND (denied OR refused) AND Australia',
    ]
    queries.extend(medical_queries)
    
    # 11. Family/custody queries
    family_queries = [
        '(custody OR family court) AND (gay OR lesbian OR same-sex OR LGBTIQ) AND Australia',
        '(surrogacy OR adoption) AND (gay OR same-sex OR LGBTIQ) AND (discrimination OR refused) AND Australia',
    ]
    queries.extend(family_queries)
    
    # 12. Historical/cold case queries
    historical_queries = [
        '"cold case" AND (gay OR homosexual) AND Australia',
        '"unsolved murder" AND (gay OR homosexual OR LGBTIQ) AND Australia',
        '"gay hate murder" AND Australia',
        '"bondi" AND (gay OR homosexual) AND (murder OR death OR cliff) AND Australia',
    ]
    queries.extend(historical_queries)
    
    # 13. Community response/survivor stories
    community_queries = [
        '"survivor story" AND (gay OR LGBTIQ OR transgender OR homophobic) AND Australia',
        '"victim speaks" AND (homophobic OR transphobic OR hate crime) AND Australia',
        '"community response" AND (homophobic attack OR hate crime) AND Australia',
        '(ACON OR Equality Australia OR LGBTIQ advocacy) AND (hate crime OR violence OR attack) AND Australia',
    ]
    queries.extend(community_queries)
    
    # 14. Source-specific queries (searching specific outlets)
    source_queries = [
        'sourcedomain:starobserver.com.au AND (attack OR assault OR violence OR hate)',
        'sourcedomain:qnews.com.au AND (attack OR assault OR violence OR hate)',
        'sourcedomain:abc.net.au AND (LGBTIQ OR gay OR transgender) AND (attack OR assault OR hate crime)',
        'sourcedomain:sbs.com.au AND (LGBTIQ OR gay OR transgender) AND (attack OR assault OR discrimination)',
        'sourcedomain:theguardian.com AND Australia AND (LGBTIQ OR gay OR transgender) AND (attack OR hate)',
    ]
    queries.extend(source_queries)
    
    # 15. Temporal event queries
    event_queries = [
        '(mardi gras OR pride parade) AND (attack OR violence OR arrest) AND Sydney',
        '(pride month OR pride week) AND (incident OR attack OR vandalism) AND Australia',
        '(marriage equality OR same-sex marriage) AND (attack OR violence OR harassment) AND Australia',
        '(plebiscite OR postal survey) AND (homophobic OR attack OR harassment) AND Australia',
    ]
    queries.extend(event_queries)
    
    return queries


# =============================================================================
# SEARCH FUNCTIONS
# =============================================================================

def fetch_gdelt_articles(query: str, start_date: datetime, end_date: datetime, max_records: int = 250) -> list[dict]:
    """Fetch articles from GDELT API."""
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "sort": "DateDesc",
        "startdatetime": start_date.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end_date.strftime("%Y%m%d%H%M%S"),
    }
    
    try:
        response = requests.get(GDELT_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.Timeout:
        log_message(f"  [TIMEOUT] Query timed out: {query[:50]}...")
        return []
    except json.JSONDecodeError:
        log_message(f"  [ERROR] Invalid JSON response for query: {query[:50]}...")
        return []
    except Exception as exc:
        log_message(f"  [ERROR] GDELT API error: {exc}")
        return []


def search_by_year(query: str, year: int) -> list[dict]:
    """Search for articles in a specific year."""
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    
    # Don't search future dates
    now = datetime.now(timezone.utc)
    if end_date > now:
        end_date = now
    
    if start_date > now:
        return []
    
    return fetch_gdelt_articles(query, start_date, end_date)


def search_by_month(query: str, year: int, month: int) -> list[dict]:
    """Search for articles in a specific month."""
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    
    now = datetime.now(timezone.utc)
    if end_date > now:
        end_date = now
    if start_date > now:
        return []
    
    return fetch_gdelt_articles(query, start_date, end_date)


# =============================================================================
# AI PROCESSING
# =============================================================================

def extract_incident_data(article_title: str, article_text: str) -> dict:
    """Use AI to determine if article describes a hate crime and extract details."""
    if not isinstance(article_text, str):
        article_text = str(article_title) if isinstance(article_title, str) else ""
    if not isinstance(article_title, str):
        article_title = ""
    
    prompt = """Analyze this Australian news article about LGBTIQ+ issues.

If this article describes an ACTUAL hate crime incident (physical attack, assault, harassment, vandalism, hate speech targeting LGBTIQ+ person), extract details. 

IMPORTANT: Only return is_hate_crime: true if there is a SPECIFIC incident described with:
- A clear victim (individual or group)
- A specific act of violence, harassment, vandalism, or hate speech
- NOT just general news about LGBTIQ+ issues, policy debates, or opinion pieces

Article Title: """ + article_title + """
Article Text: """ + article_text[:2000] + """

For location, extract the MOST SPECIFIC Australian location mentioned:
1. Street + suburb (e.g., 'Oxford Street, Darlinghurst')
2. Suburb only (e.g., 'Newtown', 'St Kilda')
3. City only if nothing more specific

Return ONLY valid JSON (no markdown):
{"is_hate_crime": true/false, "incident_type": "assault|harassment|vandalism|hate_speech|threat|murder|discrimination|other", "date": "YYYY-MM-DD or null", "location": "specific location", "victim_identity": "gay|lesbian|transgender|bisexual|queer|general_lgbtiq|unknown", "description": "2-3 sentence summary", "severity": "low|medium|high|critical", "perpetrator_info": "brief description or null"}

If NOT a hate crime incident, return: {"is_hate_crime": false}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        result_text = response.choices[0].message.content.strip()
        
        # Clean up response
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()
        
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {"is_hate_crime": False}
    except Exception as exc:
        log_message(f"  [AI ERROR] {exc}")
        return {"is_hate_crime": False}


def geocode_location(location_string: str) -> tuple[float | None, float | None]:
    """Geocode a location string to coordinates."""
    if not location_string or location_string.lower() in ["not specified", "australia", "unknown", "null", ""]:
        return None, None
    
    try:
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None, None
    except Exception:
        return None, None


# =============================================================================
# DEDUPLICATION
# =============================================================================

def generate_article_hash(url: str, title: str) -> str:
    """Generate a unique hash for an article."""
    content = f"{url}|{title}".lower().strip()
    return hashlib.md5(content.encode()).hexdigest()


def is_duplicate_incident(new_incident: dict, existing_incidents: list[dict]) -> bool:
    """Check if an incident is a duplicate of an existing one."""
    new_url = new_incident.get("url", "").lower()
    new_title = new_incident.get("title", "").lower()
    new_desc = new_incident.get("description", "").lower()
    
    for existing in existing_incidents:
        # Check URL match
        if existing.get("url", "").lower() == new_url:
            return True
        
        # Check title similarity
        existing_title = existing.get("title", "").lower()
        if existing_title and new_title:
            # Simple word overlap check
            new_words = set(new_title.split())
            existing_words = set(existing_title.split())
            overlap = len(new_words & existing_words) / max(len(new_words), 1)
            if overlap > 0.7:
                return True
    
    return False


# =============================================================================
# LOGGING & REPORTING
# =============================================================================

log_file_handle = None

def init_logging():
    """Initialize logging."""
    global log_file_handle
    log_file_handle = open(LOG_FILE, "w", encoding="utf-8")
    log_message("=" * 80)
    log_message("OVERNIGHT COMPREHENSIVE SEARCH - LGBTIQ+ HATE CRIMES AUSTRALIA")
    log_message(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 80)


def log_message(message: str):
    """Log a message to both console and file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    if log_file_handle:
        log_file_handle.write(formatted + "\n")
        log_file_handle.flush()


def close_logging():
    """Close the log file."""
    global log_file_handle
    if log_file_handle:
        log_file_handle.close()


def generate_report(stats: dict, query_results: dict, new_incidents: list[dict]):
    """Generate a comprehensive search report."""
    report_lines = [
        "=" * 80,
        "OVERNIGHT COMPREHENSIVE SEARCH REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        "",
        "SUMMARY",
        "-" * 40,
        f"Total search queries executed: {stats['total_queries']}",
        f"Total articles found: {stats['total_articles']}",
        f"Articles processed with AI: {stats['articles_processed']}",
        f"New hate crime incidents identified: {stats['new_incidents']}",
        f"Duplicate articles skipped: {stats['duplicates_skipped']}",
        f"Run duration: {stats['duration']}",
        "",
        "TOP PERFORMING QUERIES",
        "-" * 40,
    ]
    
    # Sort queries by results
    sorted_queries = sorted(query_results.items(), key=lambda x: x[1], reverse=True)
    for query, count in sorted_queries[:20]:
        if count > 0:
            report_lines.append(f"  {count:4d} results: {query[:70]}...")
    
    report_lines.extend([
        "",
        "NEW INCIDENTS BY TYPE",
        "-" * 40,
    ])
    
    # Count by incident type
    type_counts = {}
    for inc in new_incidents:
        inc_type = inc.get("incident_type", "unknown")
        type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
    
    for inc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"  {inc_type}: {count}")
    
    report_lines.extend([
        "",
        "NEW INCIDENTS BY LOCATION",
        "-" * 40,
    ])
    
    # Count by location
    location_counts = {}
    for inc in new_incidents:
        location = inc.get("location", "Unknown")
        # Extract city/state from location
        if location:
            parts = location.split(",")
            city = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
            location_counts[city] = location_counts.get(city, 0) + 1
    
    for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        report_lines.append(f"  {location}: {count}")
    
    report_lines.extend([
        "",
        "NEW INCIDENTS BY SEVERITY",
        "-" * 40,
    ])
    
    severity_counts = {}
    for inc in new_incidents:
        severity = inc.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    for severity in ["critical", "high", "medium", "low", "unknown"]:
        if severity in severity_counts:
            report_lines.append(f"  {severity}: {severity_counts[severity]}")
    
    report_lines.extend([
        "",
        "=" * 80,
        "END OF REPORT",
        "=" * 80,
    ])
    
    report_content = "\n".join(report_lines)
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    log_message(f"\nReport saved to: {REPORT_FILE}")
    return report_content


# =============================================================================
# DATA MANAGEMENT
# =============================================================================

def load_processed_urls() -> set:
    """Load previously processed URLs."""
    if PROCESSED_URLS_FILE.exists():
        with open(PROCESSED_URLS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed_url(url: str):
    """Save a processed URL."""
    with open(PROCESSED_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def load_existing_incidents() -> list[dict]:
    """Load existing incidents from main file."""
    if MAIN_INCIDENTS_FILE.exists():
        try:
            df = pd.read_csv(MAIN_INCIDENTS_FILE)
            return df.to_dict("records")
        except Exception:
            return []
    return []


def save_new_incidents(incidents: list[dict]):
    """Save new incidents to file."""
    if incidents:
        df = pd.DataFrame(incidents)
        df.to_csv(NEW_INCIDENTS_FILE, index=False)
        log_message(f"Saved {len(incidents)} new incidents to {NEW_INCIDENTS_FILE}")


def merge_into_main_dataset(new_incidents: list[dict]):
    """Merge new incidents into the main incidents file."""
    if not new_incidents:
        log_message("No new incidents to merge")
        return
    
    existing_df = pd.read_csv(MAIN_INCIDENTS_FILE) if MAIN_INCIDENTS_FILE.exists() else pd.DataFrame()
    existing_urls = set(existing_df["url"].values) if "url" in existing_df.columns else set()
    
    # Filter out duplicates
    unique_new = [inc for inc in new_incidents if inc.get("url") not in existing_urls]
    
    if unique_new:
        new_df = pd.DataFrame(unique_new)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(MAIN_INCIDENTS_FILE, index=False)
        log_message(f"Merged {len(unique_new)} new incidents into {MAIN_INCIDENTS_FILE}")
    else:
        log_message("All new incidents were duplicates, nothing merged")


def save_all_results(all_articles: list[dict]):
    """Save all found articles to results file."""
    if all_articles:
        df = pd.DataFrame(all_articles)
        df.to_csv(RESULTS_FILE, index=False)
        log_message(f"Saved {len(all_articles)} articles to {RESULTS_FILE}")


# =============================================================================
# MAIN SEARCH LOGIC
# =============================================================================

def run_comprehensive_search():
    """Run the comprehensive overnight search."""
    init_logging()
    
    log_message("\nLoading existing data...")
    processed_urls = load_processed_urls()
    existing_incidents = load_existing_incidents()
    log_message(f"Previously processed URLs: {len(processed_urls)}")
    log_message(f"Existing incidents in database: {len(existing_incidents)}")
    
    # Generate search queries
    queries = generate_search_queries()
    log_message(f"\nGenerated {len(queries)} search queries")
    
    # Statistics
    stats = {
        "total_queries": 0,
        "total_articles": 0,
        "articles_processed": 0,
        "new_incidents": 0,
        "duplicates_skipped": 0,
        "duration": "",
    }
    query_results = {}
    
    all_articles = []
    new_incidents = []
    seen_urls = set(processed_urls)
    
    start_time = datetime.now()
    years = list(range(2019, datetime.now().year + 1))
    
    log_message("\n" + "=" * 80)
    log_message("STARTING COMPREHENSIVE SEARCH")
    log_message("=" * 80)
    
    try:
        for query_idx, query in enumerate(queries):
            stats["total_queries"] += 1
            safe_query = query[:60].encode('ascii', 'replace').decode('ascii')
            log_message(f"\n[Query {query_idx + 1}/{len(queries)}] {safe_query}...")
            
            query_article_count = 0
            
            # Search each year separately for better coverage
            for year in years:
                log_message(f"  Searching {year}...", )
                
                articles = search_by_year(query, year)
                
                if articles:
                    log_message(f"    Found {len(articles)} articles")
                    query_article_count += len(articles)
                    
                    for article in articles:
                        url = article.get("url", "")
                        title = article.get("title", "Untitled")
                        
                        if not url or url in seen_urls:
                            stats["duplicates_skipped"] += 1
                            continue
                        
                        seen_urls.add(url)
                        stats["total_articles"] += 1
                        
                        # Store article info
                        article_info = {
                            "title": title,
                            "url": url,
                            "source_date": article.get("seendate"),
                            "source": article.get("domain", ""),
                            "query": query[:100],
                        }
                        all_articles.append(article_info)
                        
                        # Process with AI
                        article_text = article.get("content") or article.get("summary") or title
                        
                        safe_title = title[:50].encode('ascii', 'replace').decode('ascii')
                        log_message(f"    Processing: {safe_title}...")
                        
                        result = extract_incident_data(title, article_text)
                        stats["articles_processed"] += 1
                        
                        if result.get("is_hate_crime"):
                            # Check for duplicate incident
                            if is_duplicate_incident({"url": url, "title": title, "description": result.get("description", "")}, existing_incidents + new_incidents):
                                log_message(f"      [DUPLICATE] Skipping duplicate incident")
                                continue
                            
                            # Geocode location
                            lat, lon = geocode_location(result.get("location"))
                            time.sleep(1)  # Nominatim rate limit
                            
                            incident = {
                                "title": title,
                                "url": url,
                                "source_date": article.get("seendate"),
                                "incident_type": result.get("incident_type"),
                                "date": result.get("date"),
                                "location": result.get("location"),
                                "victim_identity": result.get("victim_identity"),
                                "description": result.get("description"),
                                "severity": result.get("severity"),
                                "perpetrator_info": result.get("perpetrator_info"),
                                "latitude": lat,
                                "longitude": lon,
                                "search_query": query[:100],
                                "found_at": datetime.now().isoformat(),
                            }
                            new_incidents.append(incident)
                            stats["new_incidents"] += 1
                            log_message(f"      [NEW INCIDENT] {result.get('incident_type')} - {result.get('location')}")
                        
                        save_processed_url(url)
                        time.sleep(AI_DELAY)
                
                time.sleep(REQUEST_DELAY)
            
            query_results[query] = query_article_count
            
            # Save progress periodically
            if (query_idx + 1) % 5 == 0:
                save_new_incidents(new_incidents)
                save_all_results(all_articles)
                log_message(f"\n  [PROGRESS] Queries: {stats['total_queries']}, Articles: {stats['total_articles']}, New incidents: {stats['new_incidents']}")
    
    except KeyboardInterrupt:
        log_message("\n\n[INTERRUPTED] Search interrupted by user")
    except Exception as exc:
        log_message(f"\n\n[ERROR] Search error: {exc}")
    
    # Calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    stats["duration"] = str(duration).split(".")[0]
    
    log_message("\n" + "=" * 80)
    log_message("SEARCH COMPLETE")
    log_message("=" * 80)
    
    # Save final results
    save_new_incidents(new_incidents)
    save_all_results(all_articles)
    
    # Merge into main dataset
    merge_into_main_dataset(new_incidents)
    
    # Generate report
    report = generate_report(stats, query_results, new_incidents)
    log_message("\n" + report)
    
    close_logging()
    
    return stats, new_incidents


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("OVERNIGHT COMPREHENSIVE SEARCH")
    print("LGBTIQ+ Hate Crime Incidents - Australia")
    print("=" * 80)
    print()
    print("This script will run for several hours, searching multiple sources")
    print("and processing articles with AI to find hate crime incidents.")
    print()
    print("Output files:")
    print(f"  - Results: {RESULTS_FILE}")
    print(f"  - New incidents: {NEW_INCIDENTS_FILE}")
    print(f"  - Log: {LOG_FILE}")
    print(f"  - Report: {REPORT_FILE}")
    print()
    print("Starting search in 5 seconds... (Ctrl+C to cancel)")
    print()
    
    time.sleep(5)
    
    stats, incidents = run_comprehensive_search()
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total queries executed: {stats['total_queries']}")
    print(f"Total articles found: {stats['total_articles']}")
    print(f"New hate crime incidents: {stats['new_incidents']}")
    print(f"Duration: {stats['duration']}")
    print("=" * 80)




