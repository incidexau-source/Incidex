import json
import os
import time
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd

DATA_PATH = os.path.join("data", "incidents_in_progress.csv")
REPORT_DIR = os.path.join("data", "quality_reports")
GENERIC_LOCATIONS = {
    "",
    "n/a",
    "na",
    "none",
    "not available",
    "not specified",
    "unknown",
    "unspecified",
    "specific location not mentioned",
    "various locations",
    "australia",
}
GENERIC_CITIES = {
    "sydney",
    "melbourne",
    "brisbane",
    "perth",
    "adelaide",
    "hobart",
    "darwin",
    "canberra",
}


def ensure_report_dir() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)


def normalize_location(value: str) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def is_specific_location(location: str) -> bool:
    """Heuristic that prefers suburb/street/venue over generic city/country."""
    if not location:
        return False

    canonical = location.lower().strip()
    if canonical in GENERIC_LOCATIONS:
        return False
    if canonical in GENERIC_CITIES:
        return False

    # Consider entries with commas, slashes, or street keywords as specific.
    street_tokens = [
        "st",
        "street",
        "rd",
        "road",
        "ave",
        "avenue",
        "blvd",
        "lane",
        "ln",
        "ct",
        "court",
        "plaza",
        "pl",
        "square",
        "station",
        "park",
        "beach",
        "mall",
        "university",
        "school",
        "club",
        "bar",
        "pub",
        "hotel",
    ]

    if any(token in canonical for token in street_tokens):
        return True

    if "," in canonical or "/" in canonical:
        return True

    # Treat multiword suburbs (e.g., "Newtown NSW") as specific.
    if len(canonical.split()) >= 2:
        return True

    # Single-word names that are not known generic cities are treated as specific suburbs.
    return True


def summarize_incident_types(df: pd.DataFrame) -> List[Tuple[str, int]]:
    counts = Counter(
        str(value).strip().lower()
        for value in df.get("incident_type", [])
        if isinstance(value, str) and value.strip()
    )
    return counts.most_common(5)


def summarize_geography(df: pd.DataFrame) -> List[Tuple[str, int]]:
    counts = Counter(
        normalize_location(loc)
        for loc in df.get("location", [])
        if normalize_location(loc)
    )
    return counts.most_common(5)


def build_report(df: pd.DataFrame) -> Dict:
    total_incidents = len(df)

    locations = [normalize_location(loc) for loc in df.get("location", [])]
    specific_flags = [is_specific_location(loc) for loc in locations]
    specific_count = sum(specific_flags)

    location_coverage = {
        "total_with_locations": sum(bool(loc) for loc in locations),
        "specific_count": specific_count,
        "percent_specific": round(
            (specific_count / total_incidents) * 100, 2
        )
        if total_incidents
        else 0.0,
    }

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_incidents": total_incidents,
        "location_quality": location_coverage,
        "incident_types_top5": summarize_incident_types(df),
        "geographic_distribution_top5": summarize_geography(df),
    }


def write_report(report: Dict) -> str:
    ensure_report_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(REPORT_DIR, f"quality_report_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return out_path


def load_incidents() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()
    return pd.read_csv(DATA_PATH)


def monitor_loop(interval_seconds: int) -> None:
    print("Starting data quality monitor...")
    print(f"Interval: {interval_seconds} seconds")

    while True:
        df = load_incidents()
        if df.empty:
            print("[WARN] incidents_in_progress.csv not found or empty.")
        else:
            report = build_report(df)
            report_path = write_report(report)
            print(f"[INFO] Report written to {report_path}")
            print(
                f"  Incidents: {report['total_incidents']} | "
                f"Specific locations: {report['location_quality']['percent_specific']}%"
            )
        time.sleep(interval_seconds)


if __name__ == "__main__":
    interval = int(os.environ.get("QUALITY_MONITOR_INTERVAL_SECONDS", "3600"))
    monitor_loop(interval)

