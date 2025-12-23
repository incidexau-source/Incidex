"""
Scraper for Australian LGBTIQ+ news sources to find hate crime incidents.
Searches queer-specific news outlets from 2019 to present.
"""

import json
import time
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

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "queer_news_incidents.csv"
PROGRESS_FILE = DATA_DIR / "queer_news_progress.csv"
PROCESSED_URLS_FILE = DATA_DIR / "queer_news_processed_urls.txt"

client = OpenAI(api_key=OPENAI_API_KEY)
geolocator = Nominatim(user_agent="lgbtiq-queer-news-scraper")

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Australian LGBTIQ+ news sources and domains
QUEER_NEWS_SOURCES = [
    "starobserver.com.au",      # Star Observer - Australia's longest-running LGBTIQ+ publication
    "qnews.com.au",             # QNews - Queensland LGBTIQ+ news
    "samesame.com.au",          # SameSame - LGBTIQ+ news and lifestyle
    "dnamagazine.com.au",       # DNA Magazine
    "lotl.com",                 # LOTL - Lesbians on the Loose
    "joymelbourne.org.au",      # JOY 94.9 Melbourne
    "2ser.com",                 # 2SER Sydney (LGBTIQ+ programming)
    "gaynewsnetwork.com.au",    # Gay News Network
    "outnewsglobal.com",        # Out News Global
    "pinknews.co.uk",           # Pink News (covers Australia)
]

# Expanded search queries for hate crimes
SEARCH_QUERIES = [
    # Direct hate crime terms
    '("hate crime" OR "homophobic attack" OR "transphobic attack" OR "anti-gay attack") AND Australia',
    '("bashing" OR "assault" OR "violence") AND (LGBTIQ OR LGBT OR gay OR lesbian OR transgender OR queer) AND Australia',
    '("harassment" OR "threat" OR "intimidation") AND (LGBTIQ OR LGBT OR gay OR lesbian OR transgender OR queer) AND Australia',
    '("vandalism" OR "graffiti" OR "property damage") AND (rainbow OR pride OR LGBTIQ) AND Australia',
    # Specific source searches
    'sourcedomain:starobserver.com.au AND (attack OR assault OR violence OR hate OR harassment OR threat)',
    'sourcedomain:qnews.com.au AND (attack OR assault OR violence OR hate OR harassment OR threat)',
    'sourcedomain:pinknews.co.uk AND Australia AND (attack OR assault OR violence OR hate)',
]


def fetch_gdelt_articles(query: str, start_date: datetime, end_date: datetime, max_records: int = 250) -> list[dict]:
    """Fetch articles from GDELT API for a given query and date range."""
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
        response = requests.get(GDELT_URL, params=params, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as exc:
        print(f"  [ERROR] GDELT API error: {exc}")
        return []


def fetch_by_month(year: int, month: int) -> list[dict]:
    """Fetch all articles for a specific month across all queries."""
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

    all_articles = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        articles = fetch_gdelt_articles(query, start_date, end_date)
        for article in articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(article)
        time.sleep(1)  # Rate limiting between queries

    return all_articles


def download_article_text(url: str) -> str:
    """Fetch article text from URL."""
    if not url:
        return ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=20, headers=headers)
        response.raise_for_status()
        return response.text[:5000]
    except Exception:
        return ""


def extract_incident_data(article_title: str, article_text: str) -> dict:
    """Use AI to determine if article describes a hate crime and extract details."""
    if not isinstance(article_text, str):
        article_text = str(article_title) if isinstance(article_title, str) else ""
    if not isinstance(article_title, str):
        article_title = ""

    prompt = "Analyze this Australian news article about LGBTIQ+ issues.\n\n"
    prompt += (
        "If this article describes an ACTUAL hate crime incident (physical attack, "
        "assault, harassment, vandalism, hate speech targeting LGBTIQ+ person), "
        "extract details. If it's just general news about LGBTIQ+ issues, "
        "discrimination debates, or policy discussions, return null.\n\n"
    )
    prompt += f"Article Title: {article_title}\n"
    prompt += f"Article Text: {article_text[:1500]}\n\n"
    prompt += "CRITICAL: For location, extract the MOST SPECIFIC location mentioned in the article. Priority order:\n"
    prompt += "1. Street name and suburb (e.g., 'Oxford Street, Darlinghurst' or 'Smith Street, Collingwood')\n"
    prompt += "2. Suburb/neighborhood name (e.g., 'Newtown', 'Fitzroy', 'Surfers Paradise')\n"
    prompt += "3. Specific venue/landmark (e.g., 'Sydney Opera House', 'Melbourne Central Station')\n"
    prompt += "4. Only if none of the above are mentioned, use city name (e.g., 'Sydney', 'Melbourne')\n"
    prompt += "NEVER use generic terms like 'not specified', 'Australia', or leave it blank.\n\n"
    prompt += "Return ONLY valid JSON (no markdown, no explanation):\n"
    prompt += (
        '{"is_hate_crime": true/false, "incident_type": "assault|harassment|vandalism|'
        'hate_speech|threat|other", "date": "YYYY-MM-DD or null", "location": "MOST '
        'SPECIFIC location", "victim_identity": "gay|lesbian|transgender|bisexual|queer|'
        'general_lgbtiq|unknown", "description": "2-3 sentence summary", "severity": '
        '"low|medium|high", "perpetrator_info": "brief description if mentioned, else null"}\n\n'
    )
    prompt += 'If NOT a hate crime incident, return: {"is_hate_crime": false}'

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        return json.loads(result_text)
    except json.JSONDecodeError as exc:
        print(f"  [WARN] JSON parse error: {exc}")
        return {"is_hate_crime": False}
    except Exception as exc:
        print(f"  [ERROR] OpenAI API error: {exc}")
        return {"is_hate_crime": False}


def geocode_location(location_string: str) -> tuple[float | None, float | None]:
    """Geocode a location string to coordinates."""
    if not location_string or location_string.lower() in ["not specified", "australia", "unknown"]:
        return None, None

    try:
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        if location:
            return location.latitude, location.longitude
        print(f"  [WARN] Unable to geocode: {location_string}")
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        print(f"  [WARN] Geocoding error for {location_string}: {exc}")
        return None, None


def load_processed_urls() -> set:
    """Load previously processed URLs."""
    if PROCESSED_URLS_FILE.exists():
        with open(PROCESSED_URLS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed_url(url: str):
    """Append a URL to the processed URLs file."""
    with open(PROCESSED_URLS_FILE, "a") as f:
        f.write(url + "\n")


def load_existing_incidents() -> list[dict]:
    """Load existing incidents from progress file."""
    if PROGRESS_FILE.exists():
        try:
            df = pd.read_csv(PROGRESS_FILE)
            return df.to_dict("records")
        except Exception:
            return []
    return []


def save_incidents(incidents: list[dict], final: bool = False):
    """Save incidents to CSV."""
    df = pd.DataFrame(incidents)
    if final:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n[INFO] Final results saved to: {OUTPUT_FILE}")
    else:
        df.to_csv(PROGRESS_FILE, index=False)


def merge_with_main_incidents(new_incidents: list[dict]):
    """Merge new incidents with the main incidents_in_progress.csv file."""
    main_file = DATA_DIR / "incidents_in_progress.csv"
    
    if main_file.exists():
        existing_df = pd.read_csv(main_file)
        existing_urls = set(existing_df["url"].values)
    else:
        existing_df = pd.DataFrame()
        existing_urls = set()

    # Filter out duplicates
    unique_new = [inc for inc in new_incidents if inc.get("url") not in existing_urls]
    
    if unique_new:
        new_df = pd.DataFrame(unique_new)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.to_csv(main_file, index=False)
        print(f"\n[INFO] Added {len(unique_new)} new incidents to {main_file}")
    else:
        print("\n[INFO] No new unique incidents to add to main file")


def main():
    print("=" * 70)
    print("QUEER NEWS SOURCES SCRAPER - LGBTIQ+ HATE CRIMES IN AUSTRALIA")
    print("=" * 70)
    print(f"\nSearching Australian LGBTIQ+ news sources for the last 5 years...")
    print(f"Sources: {', '.join(QUEER_NEWS_SOURCES[:5])}...")
    print()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load previous progress
    processed_urls = load_processed_urls()
    incidents = load_existing_incidents()
    
    print(f"Previously processed: {len(processed_urls)} URLs")
    print(f"Previously found: {len(incidents)} incidents")
    print()

    # Define date range: 2019 to present (extended range)
    end_year = datetime.now().year
    start_year = 2019  # Extended back to 2019

    total_articles_found = 0
    total_new_incidents = 0

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            # Skip future months
            if year == end_year and month > datetime.now().month:
                continue

            print(f"[{year}-{month:02d}] Fetching articles...", end=" ", flush=True)
            articles = fetch_by_month(year, month)
            print(f"Found {len(articles)} articles")

            if not articles:
                time.sleep(1)
                continue

            total_articles_found += len(articles)

            for idx, article in enumerate(articles):
                url = article.get("url", "")
                title = article.get("title", "Untitled")

                if url in processed_urls:
                    continue

                # Get article text
                article_text = article.get("content") or article.get("summary") or ""
                if not article_text:
                    article_text = download_article_text(url)

                # Sanitize title for console output
                safe_title = title[:60].encode('ascii', 'replace').decode('ascii')
                print(f"  [{idx+1}/{len(articles)}] Processing: {safe_title}...", end=" ", flush=True)

                result = extract_incident_data(title, article_text)

                # Handle None result from API errors
                if result is None:
                    result = {"is_hate_crime": False}

                if result.get("is_hate_crime"):
                    lat, lon = geocode_location(result.get("location"))
                    time.sleep(1)  # Nominatim rate limiting

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
                    }
                    incidents.append(incident)
                    total_new_incidents += 1
                    print(f"[HATE CRIME] ({total_new_incidents} new)")
                else:
                    print("[SKIP]")

                processed_urls.add(url)
                save_processed_url(url)

                time.sleep(RATE_LIMIT_DELAY)

            # Save progress after each month
            if incidents:
                save_incidents(incidents)
                print(f"  → Progress saved: {len(incidents)} total incidents\n")

            time.sleep(2)  # Rate limiting between months

    # Final save
    if incidents:
        save_incidents(incidents, final=True)
        merge_with_main_incidents(incidents)

    print("\n" + "=" * 70)
    print("QUEER NEWS SCRAPER COMPLETE")
    print("=" * 70)
    print(f"Total articles scanned: {total_articles_found}")
    print(f"New hate crime incidents found: {total_new_incidents}")
    print(f"Total incidents in queer news file: {len(incidents)}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()

