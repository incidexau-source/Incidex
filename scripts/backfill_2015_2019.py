"""
Backfill Script for LGBTIQ+ Hate Crime Incidents: 2015-2019

This script fills the gap in historical data by searching for hate crime
incidents from 2015-2019, complementing the existing 2020-2025 dataset.

Features:
- Year-by-year temporal search (2015, 2016, 2017, 2018, 2019)
- 50+ search query combinations
- Multi-source news archive search
- AI filtering and deduplication
- Geocoding of new incidents
- Merge with existing dataset
- Data quality reporting

Run time: 3-6 hours
"""

import json
import time
import hashlib
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

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Output files
RAW_RESULTS_FILE = DATA_DIR / "backfill_2015_2019_raw.csv"
INCIDENTS_FILE = DATA_DIR / "backfill_2015_2019_incidents.csv"
PROGRESS_FILE = DATA_DIR / "backfill_progress.csv"
PROCESSED_URLS_FILE = DATA_DIR / "backfill_processed_urls.txt"
LOG_FILE = LOGS_DIR / f"backfill_log_{RUN_TIMESTAMP}.txt"
REPORT_FILE = DATA_DIR / "backfill_search_report.txt"
MAIN_INCIDENTS_FILE = DATA_DIR / "incidents_in_progress.csv"
COMPLETE_DATASET_FILE = DATA_DIR / "incidents_2015_2025_complete.csv"

# API Configuration
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
REQUEST_DELAY = 3
AI_DELAY = 1

# Initialize clients
client = OpenAI(api_key=OPENAI_API_KEY)
geolocator = Nominatim(user_agent="lgbtiq-backfill-2015-2019")

# Years to backfill
BACKFILL_YEARS = [2015, 2016, 2017, 2018, 2019]

# =============================================================================
# SEARCH QUERIES - Comprehensive Coverage for 2015-2019
# =============================================================================

def generate_backfill_queries():
    """Generate comprehensive search queries for 2015-2019 period."""
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
        '"poofter bashing" AND Australia',  # Australian slang term
    ]
    queries.extend(direct_queries)
    
    # 2. Identity + violence combinations
    identity_violence = [
        '"gay man" AND (attacked OR assaulted OR beaten OR stabbed OR murdered) AND Australia',
        '"lesbian" AND (attacked OR assaulted OR beaten) AND Australia',
        '"transgender" AND (attacked OR assaulted OR beaten OR killed) AND Australia',
        '"trans woman" AND (attacked OR assaulted OR murdered) AND Australia',
        '"trans man" AND (attacked OR assaulted) AND Australia',
        '"drag queen" AND (attacked OR assaulted OR harassed) AND Australia',
        '"non-binary" AND (attacked OR assaulted OR harassed) AND Australia',
        '"same-sex couple" AND (attacked OR assaulted OR harassed) AND Australia',
    ]
    queries.extend(identity_violence)
    
    # 3. Location-specific queries (LGBTIQ hotspots)
    locations = [
        ("Oxford Street", "Sydney"),
        ("Darlinghurst", "Sydney"),
        ("Newtown", "Sydney"),
        ("Kings Cross", "Sydney"),
        ("Surry Hills", "Sydney"),
        ("St Kilda", "Melbourne"),
        ("Chapel Street", "Melbourne"),
        ("Fitzroy", "Melbourne"),
        ("Collingwood", "Melbourne"),
        ("Prahran", "Melbourne"),
        ("Fortitude Valley", "Brisbane"),
        ("West End", "Brisbane"),
        ("New Farm", "Brisbane"),
        ("Northbridge", "Perth"),
        ("Hindley Street", "Adelaide"),
        ("Salamanca", "Hobart"),
    ]
    location_queries = [
        f'(LGBTIQ OR gay OR lesbian OR transgender) AND (attack OR assault OR violence OR hate) AND "{loc[0]}"'
        for loc in locations
    ]
    queries.extend(location_queries)
    
    # 4. State-specific queries
    states = ["NSW", "Victoria", "Queensland", "Western Australia", "South Australia", "Tasmania", "ACT", "Northern Territory"]
    state_queries = [
        f'(LGBTIQ OR LGBT OR gay OR transgender) AND (hate crime OR attack OR assault OR bashing) AND "{state}"'
        for state in states
    ]
    queries.extend(state_queries)
    
    # 5. Major city queries
    cities = ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Hobart", "Darwin", "Canberra"]
    city_queries = [
        f'(gay OR lesbian OR LGBTIQ OR transgender) AND (attack OR assault OR hate crime OR violence) AND "{city}"'
        for city in cities
    ]
    queries.extend(city_queries)
    
    # 6. Venue-specific queries
    venue_queries = [
        '(gay bar OR gay club OR LGBTIQ venue) AND (attack OR assault OR violence) AND Australia',
        '(pride event OR pride march OR mardi gras) AND (attack OR violence OR incident) AND Australia',
        '(gay sauna OR gay venue) AND (attack OR assault) AND Australia',
        '(LGBTIQ community center OR queer space) AND (vandalism OR attack) AND Australia',
        '(nightclub OR pub) AND (homophobic OR gay OR LGBTIQ) AND (attack OR assault) AND Australia',
    ]
    queries.extend(venue_queries)
    
    # 7. Property crime / vandalism queries
    property_queries = [
        '"rainbow flag" AND (vandalism OR burned OR destroyed OR stolen OR defaced) AND Australia',
        '"pride flag" AND (vandalism OR defaced OR removed OR torn) AND Australia',
        '(LGBTIQ OR gay OR pride) AND (graffiti OR vandalism OR arson) AND Australia',
        '"gay venue" AND (vandalism OR attack OR fire) AND Australia',
    ]
    queries.extend(property_queries)
    
    # 8. Legal/court case queries
    legal_queries = [
        '(court case OR trial OR sentenced) AND (homophobic OR transphobic OR hate crime) AND Australia',
        '(coronial inquest OR coroner) AND (gay OR LGBTIQ OR transgender OR homosexual) AND Australia',
        '(restraining order OR AVO OR intervention order) AND (homophobic OR harassment) AND Australia',
        '"hate speech" AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(murder trial OR manslaughter) AND (gay OR homosexual OR transgender) AND Australia',
        '"gay panic" AND (defense OR defence OR trial) AND Australia',
    ]
    queries.extend(legal_queries)
    
    # 9. Workplace/school/institution queries
    institutional_queries = [
        '(workplace discrimination OR workplace harassment) AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(school bullying OR student) AND (gay OR LGBTIQ OR transgender OR homophobic) AND Australia',
        '(university OR campus) AND (homophobic OR transphobic OR LGBTIQ) AND (attack OR harassment) AND Australia',
        '(sports OR AFL OR NRL OR cricket OR rugby) AND (homophobic OR gay OR LGBTIQ) AND (abuse OR discrimination) AND Australia',
        '(teacher OR principal) AND (gay OR LGBTIQ OR transgender) AND (fired OR sacked OR dismissed) AND Australia',
    ]
    queries.extend(institutional_queries)
    
    # 10. Religious institution queries
    religious_queries = [
        '(church OR religious school OR catholic OR christian) AND (gay OR LGBTIQ OR transgender) AND (discrimination OR expelled OR fired) AND Australia',
        '(religious exemption OR religious freedom) AND (LGBTIQ OR gay OR transgender) AND Australia',
        '(priest OR pastor OR minister) AND (homophobic OR anti-gay) AND Australia',
    ]
    queries.extend(religious_queries)
    
    # 11. Medical/healthcare queries
    medical_queries = [
        '(hospital OR medical OR healthcare OR doctor) AND (transgender OR gay OR LGBTIQ) AND (discrimination OR refused) AND Australia',
        '(gender affirming OR hormone therapy OR transition) AND (denied OR refused OR discrimination) AND Australia',
        '(mental health OR psychiatrist OR psychologist) AND (gay OR LGBTIQ OR conversion) AND Australia',
    ]
    queries.extend(medical_queries)
    
    # 12. Police/justice system queries
    police_queries = [
        '(police OR officer) AND (gay OR LGBTIQ OR transgender) AND (misconduct OR assault OR harassment) AND Australia',
        '(arrest OR detained) AND (gay OR LGBTIQ OR transgender) AND (discrimination OR profiling) AND Australia',
        '(prison OR jail OR custody) AND (gay OR transgender) AND (assault OR attack) AND Australia',
    ]
    queries.extend(police_queries)
    
    # 13. Historical/cold case queries
    historical_queries = [
        '"cold case" AND (gay OR homosexual) AND Australia',
        '"unsolved murder" AND (gay OR homosexual OR LGBTIQ) AND Australia',
        '"gay hate murder" AND Australia',
        '"bondi" AND (gay OR homosexual) AND (murder OR death OR cliff OR pushed) AND Australia',
        '"marks park" AND (gay OR murder) AND Sydney',
        '"gay hate crimes" AND (1980s OR 1990s OR historic) AND Australia',
    ]
    queries.extend(historical_queries)
    
    # 14. Marriage equality era queries (2015-2017 was key period)
    marriage_equality_queries = [
        '"marriage equality" AND (attack OR violence OR harassment OR vandalism) AND Australia',
        '"same-sex marriage" AND (attack OR assault OR harassment) AND Australia',
        '(plebiscite OR postal survey OR postal vote) AND (homophobic OR attack OR harassment) AND Australia',
        '"vote no" AND (harassment OR attack OR vandalism) AND Australia',
        '"safe schools" AND (attack OR harassment OR controversy) AND Australia',
    ]
    queries.extend(marriage_equality_queries)
    
    # 15. Community response/survivor stories
    community_queries = [
        '"survivor story" AND (gay OR LGBTIQ OR transgender OR homophobic) AND Australia',
        '"victim speaks" AND (homophobic OR transphobic OR hate crime) AND Australia',
        '"community response" AND (homophobic attack OR hate crime) AND Australia',
        '(ACON OR Equality Australia OR LGBTIQ advocacy) AND (hate crime OR violence OR attack) AND Australia',
        '"vigil" AND (gay OR LGBTIQ OR transgender) AND (murder OR attack) AND Australia',
    ]
    queries.extend(community_queries)
    
    # 16. Source-specific queries
    source_queries = [
        'sourcedomain:starobserver.com.au AND (attack OR assault OR violence OR hate OR murder)',
        'sourcedomain:qnews.com.au AND (attack OR assault OR violence OR hate)',
        'sourcedomain:abc.net.au AND (LGBTIQ OR gay OR transgender) AND (attack OR assault OR hate crime)',
        'sourcedomain:sbs.com.au AND (LGBTIQ OR gay OR transgender) AND (attack OR assault OR discrimination)',
        'sourcedomain:theguardian.com AND Australia AND (LGBTIQ OR gay OR transgender) AND (attack OR hate)',
        'sourcedomain:smh.com.au AND (gay OR LGBTIQ OR transgender) AND (attack OR assault OR hate)',
        'sourcedomain:theage.com.au AND (gay OR LGBTIQ OR transgender) AND (attack OR assault OR hate)',
    ]
    queries.extend(source_queries)
    
    # 17. Mardi Gras and Pride events
    event_queries = [
        '(mardi gras OR "sydney gay") AND (attack OR violence OR arrest OR incident) AND Sydney',
        '(pride march OR pride parade) AND (attack OR violence OR incident) AND Australia',
        '(pride week OR pride month) AND (incident OR attack OR vandalism) AND Australia',
        '"fair day" AND (incident OR attack) AND Sydney',
    ]
    queries.extend(event_queries)
    
    # 18. Specific violence terms
    violence_specific = [
        '(stabbed OR stabbing) AND (gay OR LGBTIQ OR transgender OR homophobic) AND Australia',
        '(punched OR bashed OR beaten) AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(murdered OR killed OR death) AND (gay OR LGBTIQ OR transgender OR homosexual) AND Australia',
        '(sexual assault OR rape) AND (gay OR LGBTIQ OR transgender) AND Australia',
        '(harassment OR stalking OR threats) AND (gay OR LGBTIQ OR transgender) AND Australia',
    ]
    queries.extend(violence_specific)
    
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
        log_message(f"    [TIMEOUT] Query timed out")
        return []
    except json.JSONDecodeError:
        log_message(f"    [ERROR] Invalid JSON response")
        return []
    except Exception as exc:
        log_message(f"    [ERROR] GDELT API error: {exc}")
        return []


def search_year(query: str, year: int) -> list[dict]:
    """Search for articles in a specific year."""
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    return fetch_gdelt_articles(query, start_date, end_date)


def search_quarter(query: str, year: int, quarter: int) -> list[dict]:
    """Search for articles in a specific quarter of a year."""
    quarter_starts = {1: 1, 2: 4, 3: 7, 4: 10}
    quarter_ends = {1: 3, 2: 6, 3: 9, 4: 12}
    
    start_month = quarter_starts[quarter]
    end_month = quarter_ends[quarter]
    
    start_date = datetime(year, start_month, 1, tzinfo=timezone.utc)
    if end_month == 12:
        end_date = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, end_month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    
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
- NOT international incidents (must be in Australia)

Article Title: """ + article_title + """
Article Text: """ + article_text[:2000] + """

For location, extract the MOST SPECIFIC Australian location mentioned:
1. Street + suburb (e.g., 'Oxford Street, Darlinghurst')
2. Suburb only (e.g., 'Newtown', 'St Kilda')
3. City only if nothing more specific

Return ONLY valid JSON (no markdown):
{"is_hate_crime": true/false, "incident_type": "assault|harassment|vandalism|hate_speech|threat|murder|discrimination|other", "date": "YYYY-MM-DD or null", "location": "specific Australian location", "victim_identity": "gay|lesbian|transgender|bisexual|queer|general_lgbtiq|unknown", "description": "2-3 sentence summary", "severity": "low|medium|high|critical", "perpetrator_info": "brief description or null", "is_australian": true/false}

If NOT a hate crime incident OR not in Australia, return: {"is_hate_crime": false}"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=400,
        )
        result_text = response.choices[0].message.content.strip()
        
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        
        # Filter out non-Australian incidents
        if result.get("is_australian") == False:
            return {"is_hate_crime": False}
        
        return result
    except json.JSONDecodeError:
        return {"is_hate_crime": False}
    except Exception as exc:
        log_message(f"    [AI ERROR] {exc}")
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

def is_duplicate_incident(new_incident: dict, existing_incidents: list[dict]) -> bool:
    """Check if an incident is a duplicate of an existing one."""
    new_url = new_incident.get("url", "").lower()
    new_title = new_incident.get("title", "").lower()
    
    for existing in existing_incidents:
        if existing.get("url", "").lower() == new_url:
            return True
        
        existing_title = existing.get("title", "").lower()
        if existing_title and new_title:
            new_words = set(new_title.split())
            existing_words = set(existing_title.split())
            if len(new_words) > 0:
                overlap = len(new_words & existing_words) / len(new_words)
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
    log_message("BACKFILL SEARCH: 2015-2019 LGBTIQ+ HATE CRIMES AUSTRALIA")
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


def generate_report(stats: dict, year_stats: dict, new_incidents: list[dict]):
    """Generate a comprehensive backfill report."""
    report_lines = [
        "=" * 80,
        "BACKFILL SEARCH REPORT: 2015-2019",
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
        "YEAR-BY-YEAR BREAKDOWN",
        "-" * 40,
    ]
    
    for year in BACKFILL_YEARS:
        year_data = year_stats.get(year, {"articles": 0, "incidents": 0})
        report_lines.append(f"  {year}: {year_data['articles']:4d} articles, {year_data['incidents']:3d} incidents")
    
    report_lines.extend([
        "",
        "INCIDENTS BY TYPE",
        "-" * 40,
    ])
    
    type_counts = {}
    for inc in new_incidents:
        inc_type = inc.get("incident_type", "unknown")
        type_counts[inc_type] = type_counts.get(inc_type, 0) + 1
    
    for inc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"  {inc_type}: {count}")
    
    report_lines.extend([
        "",
        "INCIDENTS BY SEVERITY",
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
        "INCIDENTS BY LOCATION (Top 15)",
        "-" * 40,
    ])
    
    location_counts = {}
    for inc in new_incidents:
        location = inc.get("location", "Unknown")
        if location:
            parts = location.split(",")
            city = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
            location_counts[city] = location_counts.get(city, 0) + 1
    
    for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        report_lines.append(f"  {location}: {count}")
    
    report_lines.extend([
        "",
        "DATA QUALITY ASSESSMENT",
        "-" * 40,
    ])
    
    # Calculate completeness estimates
    total_incidents = len(new_incidents)
    geocoded = sum(1 for inc in new_incidents if inc.get("latitude"))
    with_dates = sum(1 for inc in new_incidents if inc.get("date"))
    
    report_lines.append(f"  Incidents with coordinates: {geocoded}/{total_incidents} ({100*geocoded/max(total_incidents,1):.1f}%)")
    report_lines.append(f"  Incidents with dates: {with_dates}/{total_incidents} ({100*with_dates/max(total_incidents,1):.1f}%)")
    
    # Year completeness
    report_lines.append("")
    report_lines.append("  Estimated Data Completeness by Year:")
    for year in BACKFILL_YEARS:
        year_incidents = year_stats.get(year, {}).get("incidents", 0)
        # Rough estimate: expect ~20-50 incidents per year based on 2020+ data
        completeness = min(100, year_incidents / 30 * 100)
        status = "Good" if completeness > 70 else "Partial" if completeness > 30 else "Limited"
        report_lines.append(f"    {year}: {status} ({year_incidents} incidents found)")
    
    report_lines.extend([
        "",
        "NOTES",
        "-" * 40,
        "  - Older articles (2015-2016) may have less detail available",
        "  - Some articles may be deleted or unavailable",
        "  - Marriage equality period (2017) may show spike in incidents",
        "  - Regional/rural incidents likely underrepresented",
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
    urls = set()
    
    # Load from backfill processed URLs
    if PROCESSED_URLS_FILE.exists():
        with open(PROCESSED_URLS_FILE, "r", encoding="utf-8") as f:
            urls.update(line.strip() for line in f if line.strip())
    
    # Also load from main processed URLs to avoid duplicates
    main_processed = DATA_DIR / "processed_urls.txt"
    if main_processed.exists():
        with open(main_processed, "r", encoding="utf-8") as f:
            urls.update(line.strip() for line in f if line.strip())
    
    # Load from overnight search
    overnight_processed = DATA_DIR / "overnight_processed_urls.txt"
    if overnight_processed.exists():
        with open(overnight_processed, "r", encoding="utf-8") as f:
            urls.update(line.strip() for line in f if line.strip())
    
    return urls


def save_processed_url(url: str):
    """Save a processed URL."""
    with open(PROCESSED_URLS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def load_existing_incidents() -> list[dict]:
    """Load all existing incidents from all sources."""
    all_incidents = []
    
    # Main incidents file
    if MAIN_INCIDENTS_FILE.exists():
        try:
            df = pd.read_csv(MAIN_INCIDENTS_FILE)
            all_incidents.extend(df.to_dict("records"))
        except Exception:
            pass
    
    # Overnight search incidents
    overnight_file = DATA_DIR / "overnight_search_new_incidents.csv"
    if overnight_file.exists():
        try:
            df = pd.read_csv(overnight_file)
            all_incidents.extend(df.to_dict("records"))
        except Exception:
            pass
    
    # Previous backfill incidents
    if INCIDENTS_FILE.exists():
        try:
            df = pd.read_csv(INCIDENTS_FILE)
            all_incidents.extend(df.to_dict("records"))
        except Exception:
            pass
    
    return all_incidents


def save_incidents(incidents: list[dict]):
    """Save backfill incidents to file."""
    if incidents:
        df = pd.DataFrame(incidents)
        df.to_csv(INCIDENTS_FILE, index=False)
        log_message(f"Saved {len(incidents)} incidents to {INCIDENTS_FILE}")


def save_raw_results(articles: list[dict]):
    """Save raw article results."""
    if articles:
        df = pd.DataFrame(articles)
        df.to_csv(RAW_RESULTS_FILE, index=False)


def merge_into_main_dataset(new_incidents: list[dict]):
    """Merge new incidents into the main incidents file."""
    if not new_incidents:
        log_message("No new incidents to merge")
        return
    
    existing_df = pd.read_csv(MAIN_INCIDENTS_FILE) if MAIN_INCIDENTS_FILE.exists() else pd.DataFrame()
    existing_urls = set(existing_df["url"].values) if "url" in existing_df.columns else set()
    
    unique_new = [inc for inc in new_incidents if inc.get("url") not in existing_urls]
    
    if unique_new:
        new_df = pd.DataFrame(unique_new)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(MAIN_INCIDENTS_FILE, index=False)
        log_message(f"Merged {len(unique_new)} new incidents into {MAIN_INCIDENTS_FILE}")
        
        # Also create complete 2015-2025 dataset
        combined_df.to_csv(COMPLETE_DATASET_FILE, index=False)
        log_message(f"Created complete dataset: {COMPLETE_DATASET_FILE}")
    else:
        log_message("All new incidents were duplicates, nothing merged")


# =============================================================================
# MAIN SEARCH LOGIC
# =============================================================================

def run_backfill_search():
    """Run the backfill search for 2015-2019."""
    init_logging()
    
    log_message("\nLoading existing data...")
    processed_urls = load_processed_urls()
    existing_incidents = load_existing_incidents()
    log_message(f"Previously processed URLs: {len(processed_urls)}")
    log_message(f"Existing incidents in database: {len(existing_incidents)}")
    
    queries = generate_backfill_queries()
    log_message(f"\nGenerated {len(queries)} search queries")
    
    stats = {
        "total_queries": 0,
        "total_articles": 0,
        "articles_processed": 0,
        "new_incidents": 0,
        "duplicates_skipped": 0,
        "duration": "",
    }
    
    year_stats = {year: {"articles": 0, "incidents": 0} for year in BACKFILL_YEARS}
    
    all_articles = []
    new_incidents = []
    seen_urls = set(processed_urls)
    
    start_time = datetime.now()
    
    log_message("\n" + "=" * 80)
    log_message("STARTING BACKFILL SEARCH: 2015-2019")
    log_message("=" * 80)
    
    try:
        for query_idx, query in enumerate(queries):
            stats["total_queries"] += 1
            safe_query = query[:60].encode('ascii', 'replace').decode('ascii')
            log_message(f"\n[Query {query_idx + 1}/{len(queries)}] {safe_query}...")
            
            # Search each year in the backfill range
            for year in BACKFILL_YEARS:
                log_message(f"  {year}...", )
                
                articles = search_year(query, year)
                
                if articles:
                    log_message(f"    Found {len(articles)} articles")
                    year_stats[year]["articles"] += len(articles)
                    
                    for article in articles:
                        url = article.get("url", "")
                        title = article.get("title", "Untitled")
                        
                        if not url or url in seen_urls:
                            stats["duplicates_skipped"] += 1
                            continue
                        
                        seen_urls.add(url)
                        stats["total_articles"] += 1
                        
                        article_info = {
                            "title": title,
                            "url": url,
                            "source_date": article.get("seendate"),
                            "source": article.get("domain", ""),
                            "year": year,
                            "query": query[:100],
                        }
                        all_articles.append(article_info)
                        
                        article_text = article.get("content") or article.get("summary") or title
                        
                        safe_title = title[:50].encode('ascii', 'replace').decode('ascii')
                        log_message(f"    Processing: {safe_title}...")
                        
                        result = extract_incident_data(title, article_text)
                        stats["articles_processed"] += 1
                        
                        if result.get("is_hate_crime"):
                            if is_duplicate_incident({"url": url, "title": title}, existing_incidents + new_incidents):
                                log_message(f"      [DUPLICATE] Skipping")
                                continue
                            
                            lat, lon = geocode_location(result.get("location"))
                            time.sleep(1)
                            
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
                                "year_found": year,
                                "found_at": datetime.now().isoformat(),
                            }
                            new_incidents.append(incident)
                            stats["new_incidents"] += 1
                            year_stats[year]["incidents"] += 1
                            log_message(f"      [NEW INCIDENT] {result.get('incident_type')} - {result.get('location')}")
                        
                        save_processed_url(url)
                        time.sleep(AI_DELAY)
                
                time.sleep(REQUEST_DELAY)
            
            # Save progress every 5 queries
            if (query_idx + 1) % 5 == 0:
                save_incidents(new_incidents)
                save_raw_results(all_articles)
                log_message(f"\n  [PROGRESS] Queries: {stats['total_queries']}, Articles: {stats['total_articles']}, New incidents: {stats['new_incidents']}")
    
    except KeyboardInterrupt:
        log_message("\n\n[INTERRUPTED] Search interrupted by user")
    except Exception as exc:
        log_message(f"\n\n[ERROR] Search error: {exc}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    stats["duration"] = str(duration).split(".")[0]
    
    log_message("\n" + "=" * 80)
    log_message("BACKFILL SEARCH COMPLETE")
    log_message("=" * 80)
    
    save_incidents(new_incidents)
    save_raw_results(all_articles)
    
    merge_into_main_dataset(new_incidents)
    
    report = generate_report(stats, year_stats, new_incidents)
    log_message("\n" + report)
    
    close_logging()
    
    return stats, new_incidents


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("BACKFILL SEARCH: 2015-2019")
    print("LGBTIQ+ Hate Crime Incidents - Australia")
    print("=" * 80)
    print()
    print("This script will search for hate crime incidents from 2015-2019,")
    print("filling the gap before the existing 2020-2025 dataset.")
    print()
    print(f"Years to search: {', '.join(map(str, BACKFILL_YEARS))}")
    print()
    print("Output files:")
    print(f"  - Raw results: {RAW_RESULTS_FILE}")
    print(f"  - New incidents: {INCIDENTS_FILE}")
    print(f"  - Log: {LOG_FILE}")
    print(f"  - Report: {REPORT_FILE}")
    print()
    print("Starting search in 5 seconds... (Ctrl+C to cancel)")
    print()
    
    time.sleep(5)
    
    stats, incidents = run_backfill_search()
    
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total queries executed: {stats['total_queries']}")
    print(f"Total articles found: {stats['total_articles']}")
    print(f"New hate crime incidents: {stats['new_incidents']}")
    print(f"Duration: {stats['duration']}")
    print()
    print("Year-by-year incidents:")
    for year in BACKFILL_YEARS:
        count = sum(1 for inc in incidents if inc.get("year_found") == year)
        print(f"  {year}: {count}")
    print("=" * 80)









