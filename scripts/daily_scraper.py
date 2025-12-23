import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import sys

import pandas as pd
import requests
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, RATE_LIMIT_DELAY

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "daily_incidents.csv"

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = (
    '("hate crime" OR "homophobic attack" OR "transphobic" OR '
    '"anti-gay" OR "anti-LGBT") AND Australia'
)

client = OpenAI(api_key=OPENAI_API_KEY)
geolocator = Nominatim(user_agent="lgbtiq-daily-scraper")


def fetch_recent_articles(hours_back: int, max_records: int) -> list[dict]:
    """
    Query the GDELT API for Australian LGBTIQ+ hate-crime articles
    published within the last `hours_back` hours.
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours_back)

    params = {
        "query": GDELT_QUERY,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "sort": "DateDesc",
        "startdatetime": start_time.strftime("%Y%m%d%H%M%S"),
        "enddatetime": end_time.strftime("%Y%m%d%H%M%S"),
    }

    try:
        print(
            "Fetching GDELT articles from",
            params["startdatetime"],
            "to",
            params["enddatetime"],
        )
        response = requests.get(GDELT_URL, params=params, timeout=45)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as exc:
        print(f"[ERROR] Failed to fetch daily articles: {exc}")
        return []


def download_article_text(url: str) -> str:
    """Fetch raw HTML for an article as a fallback signal for the LLM."""
    if not url:
        return ""

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.text[:5000]  # keep payload manageable
    except Exception:
        return ""


def extract_incident_data(article_title: str, article_text: str) -> dict:
    """
    Reuse the same extraction logic as scripts/process_articles.py
    to ensure output parity between historical and daily jobs.
    """
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
    prompt += f"Article Text: {article_text[:1000]}\n\n"
    prompt += "CRITICAL: For location, extract the MOST SPECIFIC location mentioned in the article. Priority order:\n"
    prompt += "1. Street name and suburb (e.g., 'Oxford Street, Darlinghurst' or 'Smith Street, Collingwood')\n"
    prompt += "2. Suburb/neighborhood name (e.g., 'Newtown', 'Fitzroy', 'Surfers Paradise')\n"
    prompt += "3. Specific venue/landmark (e.g., 'Sydney Opera House', 'Melbourne Central Station')\n"
    prompt += "4. Only if none of the above are mentioned, use city name (e.g., 'Sydney', 'Melbourne')\n"
    prompt += "NEVER use generic terms like 'not specified', 'Australia', or leave it blank. Always extract the most specific location available.\n\n"
    prompt += "Return ONLY valid JSON (no markdown, no explanation):\n"
    prompt += (
        '{"is_hate_crime": true/false, "incident_type": "assault|harassment|vandalism|'
        'hate_speech|threat|other", "date": "YYYY-MM-DD or null", "location": "MOST '
        'SPECIFIC location: street+suburb > suburb > venue > city (never generic '
        'terms)", "victim_identity": "gay|lesbian|transgender|bisexual|queer|'
        'general_lgbtiq|unknown", "description": "2-3 sentence summary", "severity": '
        '"low|medium|high", "perpetrator_info": "brief description if mentioned, else '
        'null"}\n\n'
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
        if result_text.startswith("json"):
            result_text = result_text[4:]

        return json.loads(result_text)
    except json.JSONDecodeError as exc:
        print(f"[WARN] JSON parse error: {exc}")
        return {"is_hate_crime": False}
    except Exception as exc:
        print(f"[ERROR] OpenAI API error: {exc}")
        return {"is_hate_crime": False}


def geocode_location(location_string: str) -> tuple[float | None, float | None]:
    """Mirror the geocoding logic used elsewhere in the project."""
    if not location_string:
        return None, None

    try:
        search_query = f"{location_string}, Australia"
        location = geolocator.geocode(search_query, timeout=10)
        if location:
            return location.latitude, location.longitude
        print(f"[WARN] Unable to geocode: {location_string}")
        return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        print(f"[WARN] Geocoding error for {location_string}: {exc}")
        return None, None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Daily scraper for Australian LGBTIQ+ hate crime incidents."
    )
    parser.add_argument(
        "--hours-back",
        type=int,
        default=24,
        help="How many hours of news to scan (default: 24).",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=100,
        help="Maximum number of records to fetch from GDELT (default: 100).",
    )
    return parser.parse_args()


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    args = parse_args()

    articles = fetch_recent_articles(args.hours_back, args.max_records)
    if not articles:
        print("[INFO] No articles returned by GDELT.")
        empty_df = pd.DataFrame(
            columns=[
                "title",
                "url",
                "source_date",
                "incident_type",
                "date",
                "location",
                "victim_identity",
                "description",
                "severity",
                "perpetrator_info",
                "latitude",
                "longitude",
                "processed_at",
            ]
        )
        empty_df.to_csv(OUTPUT_FILE, index=False)
        return

    print(f"[INFO] Evaluating {len(articles)} articles for hate crimes")
    incidents: list[dict] = []
    seen_urls: set[str] = set()
    processed_timestamp = datetime.now(timezone.utc).isoformat()

    for idx, article in enumerate(articles, start=1):
        title = article.get("title") or article.get("seendate") or "Untitled"
        url = article.get("url") or article.get("sourceurl")

        if url and url in seen_urls:
            print(f"[SKIP] Duplicate URL at index {idx}")
            continue

        article_text = (
            article.get("content")
            or article.get("summary")
            or article.get("excerpt")
            or ""
        )

        if not article_text:
            article_text = download_article_text(url)

        print(f"[{idx}/{len(articles)}] Processing daily article...", end=" ")
        result = extract_incident_data(title, article_text)

        if result.get("is_hate_crime"):
            lat, lon = geocode_location(result.get("location"))
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
                "processed_at": processed_timestamp,
            }
            incidents.append(incident)
            print(f"[HATE CRIME] Found ({len(incidents)} total)")
        else:
            print("[SKIP] Not a hate crime")

        if url:
            seen_urls.add(url)

        time.sleep(RATE_LIMIT_DELAY)
        # Respect Nominatim guidance
        time.sleep(1)

    df = pd.DataFrame(incidents)
    df.to_csv(OUTPUT_FILE, index=False)

    print("=" * 60)
    print("DAILY SCRAPER COMPLETE")
    print(f"Articles checked: {len(seen_urls)}")
    print(f"Hate crime incidents found: {len(incidents)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()

