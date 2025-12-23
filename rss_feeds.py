"""
RSS Feed Configuration for Sentinel LGBTIQ+ Hate Crime Mapping Project

This module defines all RSS feeds to monitor for LGBTIQ+ hate crime incidents.
Feeds are organized by source type and include metadata for filtering and attribution.

Note: Some news outlets may require API keys or have rate limits. Check each
outlet's terms of service before deploying to production.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class FeedRegion(Enum):
    """Geographic regions for feed categorization"""
    NATIONAL = "national"
    STATE = "state"
    REGIONAL = "regional"
    QUEER = "queer"


@dataclass
class RSSFeed:
    """
    RSS feed configuration with metadata
    
    Attributes:
        name: Display name for the news source
        url: RSS feed URL (Atom feeds also supported)
        region: Geographic scope (NATIONAL, STATE, REGIONAL, QUEER)
        state: Australian state/territory if applicable (NSW, VIC, QLD, etc.)
        keywords_filter: Optional list of keywords that should appear in articles
                        to reduce false positives. None means no filtering.
        enabled: Whether this feed is currently active (for easy enable/disable)
        notes: Additional notes about the feed (rate limits, special handling, etc.)
    """
    name: str
    url: str
    region: FeedRegion
    state: Optional[str] = None
    keywords_filter: Optional[list[str]] = None
    enabled: bool = True
    notes: Optional[str] = None


# =============================================================================
# NATIONAL NEWS OUTLETS
# =============================================================================

NATIONAL_FEEDS = [
    RSSFeed(
        name="ABC News Australia - National",
        url="https://www.abc.net.au/news/feed/45910/rss.xml",
        region=FeedRegion.NATIONAL,
        notes="ABC's main national RSS feed. Includes all major stories."
    ),
    # RSSFeed(
    #     name="ABC News Australia - Breaking News",
    #     url="https://www.abc.net.au/news/feed/52278/rss.xml",
    #     region=FeedRegion.NATIONAL,
    #     notes="Breaking news feed - may contain urgent hate crime reports. URL returns 404 - commented out."
    # ),
    RSSFeed(
        name="The Guardian Australia",
        url="https://www.theguardian.com/australia-news/rss",
        region=FeedRegion.NATIONAL,
        notes="Guardian Australia main RSS feed. High-quality journalism."
    ),
    # RSSFeed(
    #     name="The Guardian Australia - Society",
    #     url="https://www.theguardian.com/australia-news/society/rss",
    #     region=FeedRegion.NATIONAL,
    #     notes="Society section often covers discrimination and hate crimes. URL returns 404 - commented out."
    # ),
]


# =============================================================================
# STATE-SPECIFIC FEEDS
# =============================================================================

STATE_FEEDS = [
    # New South Wales
    # (ABC News - NSW removed - broken feed)
    # (Brisbane Times removed - broken feed)
    
    # Victoria
    RSSFeed(
        name="ABC News - VIC",
        url="https://www.abc.net.au/news/feed/45928/rss.xml",
        region=FeedRegion.STATE,
        state="VIC",
    ),
    RSSFeed(
        name="The Age",
        url="https://www.theage.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="VIC",
        notes="Major Victorian newspaper."
    ),
    
    # Queensland
    RSSFeed(
        name="ABC News - QLD",
        url="https://www.abc.net.au/news/feed/45924/rss.xml",
        region=FeedRegion.STATE,
        state="QLD",
    ),
    RSSFeed(
        name="Courier Mail",
        url="https://www.couriermail.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="QLD",
    ),
    
    # Western Australia
    RSSFeed(
        name="ABC News - WA",
        url="https://www.abc.net.au/news/feed/45932/rss.xml",
        region=FeedRegion.STATE,
        state="WA",
    ),
    RSSFeed(
        name="The West Australian",
        url="https://thewest.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="WA",
    ),
    
    # South Australia
    RSSFeed(
        name="ABC News - SA",
        url="https://www.abc.net.au/news/feed/45936/rss.xml",
        region=FeedRegion.STATE,
        state="SA",
    ),
    RSSFeed(
        name="The Advertiser",
        url="https://www.adelaidenow.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="SA",
        notes="Adelaide Now / The Advertiser RSS feed."
    ),
    
    # Tasmania
    RSSFeed(
        name="ABC News - TAS",
        url="https://www.abc.net.au/news/feed/45940/rss.xml",
        region=FeedRegion.STATE,
        state="TAS",
    ),
    RSSFeed(
        name="The Mercury",
        url="https://www.themercury.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="TAS",
        notes="Hobart-based newspaper."
    ),
    
    # Australian Capital Territory
    RSSFeed(
        name="ABC News - ACT",
        url="https://www.abc.net.au/news/feed/45944/rss.xml",
        region=FeedRegion.STATE,
        state="ACT",
    ),
    RSSFeed(
        name="The Canberra Times",
        url="https://www.canberratimes.com.au/rss.xml",
        region=FeedRegion.STATE,
        state="ACT",
    ),
    
    # Northern Territory
    RSSFeed(
        name="ABC News - NT",
        url="https://www.abc.net.au/news/feed/45948/rss.xml",
        region=FeedRegion.STATE,
        state="NT",
    ),
]


# =============================================================================
# LGBTIQ+ SPECIFIC NEWS SOURCES
# =============================================================================

QUEER_FEEDS = [
    RSSFeed(
        name="PinkNews - LGBTIQ+ News",
        url="https://www.thepinknews.com/feed/",
        region=FeedRegion.QUEER,
        notes="PinkNews RSS feed for LGBTIQ+ news coverage.",
        keywords_filter=["lgbt", "lgbtq", "lgbti", "lgbtiq", "queer", "gay", "lesbian", 
                        "trans", "transgender", "bisexual", "hate", "attack", "assault", 
                        "discrimination"]
    ),
    RSSFeed(
        name="DNA Magazine",
        url="https://www.dnamagazine.com.au/feed/",
        region=FeedRegion.QUEER,
        notes="Australian LGBTIQ+ publication. May not have RSS feed - verify URL.",
        enabled=False,  # Disable until verified
    ),
    RSSFeed(
        name="Star Observer",
        url="https://www.starobserver.com.au/feed/",
        region=FeedRegion.QUEER,
        notes="Major Australian LGBTIQ+ news outlet.",
    ),
    # (Q News removed - broken feed)
]


# =============================================================================
# ADDITIONAL REGIONAL/SPECIALTY FEEDS
# =============================================================================

REGIONAL_FEEDS = [
    RSSFeed(
        name="Newcastle Herald",
        url="https://www.newcastleherald.com.au/rss.xml",
        region=FeedRegion.REGIONAL,
        state="NSW",
    ),
    # (Geelong Advertiser removed - broken feed)
    RSSFeed(
        name="Gold Coast Bulletin",
        url="https://www.goldcoastbulletin.com.au/rss.xml",
        region=FeedRegion.REGIONAL,
        state="QLD",
    ),
]


# =============================================================================
# ALL FEEDS AGGREGATION
# =============================================================================

def get_all_feeds() -> list[RSSFeed]:
    """
    Get all configured RSS feeds that are currently enabled.
    
    Returns:
        List of RSSFeed objects with enabled=True
    """
    all_feeds = NATIONAL_FEEDS + STATE_FEEDS + QUEER_FEEDS + REGIONAL_FEEDS
    return [feed for feed in all_feeds if feed.enabled]


def get_feeds_by_region(region: FeedRegion) -> list[RSSFeed]:
    """
    Get feeds filtered by region type.
    
    Args:
        region: FeedRegion enum value
        
    Returns:
        List of enabled RSSFeed objects matching the region
    """
    all_feeds = get_all_feeds()
    return [feed for feed in all_feeds if feed.region == region]


def get_feeds_by_state(state: str) -> list[RSSFeed]:
    """
    Get feeds filtered by Australian state/territory.
    
    Args:
        state: Two-letter state code (NSW, VIC, QLD, etc.)
        
    Returns:
        List of enabled RSSFeed objects matching the state
    """
    all_feeds = get_all_feeds()
    return [feed for feed in all_feeds if feed.state == state.upper()]


def validate_feed_urls() -> dict[str, list[str]]:
    """
    Validate that all feed URLs are accessible (for testing).
    
    Returns:
        Dictionary with 'valid' and 'invalid' keys containing lists of feed names
    """
    import requests
    
    results = {"valid": [], "invalid": []}
    
    for feed in get_all_feeds():
        try:
            response = requests.get(feed.url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SentinelRSSMonitor/1.0)"
            })
            if response.status_code == 200:
                results["valid"].append(feed.name)
            else:
                results["invalid"].append(f"{feed.name} (HTTP {response.status_code})")
        except Exception as e:
            results["invalid"].append(f"{feed.name} ({str(e)})")
    
    return results


if __name__ == "__main__":
    # Quick test to list all feeds
    print("=" * 70)
    print("RSS FEED CONFIGURATION")
    print("=" * 70)
    
    all_feeds = get_all_feeds()
    print(f"\nTotal enabled feeds: {len(all_feeds)}\n")
    
    print("NATIONAL FEEDS:")
    for feed in get_feeds_by_region(FeedRegion.NATIONAL):
        print(f"  - {feed.name}")
    
    print("\nSTATE FEEDS:")
    states = {}
    for feed in get_feeds_by_region(FeedRegion.STATE):
        if feed.state:
            if feed.state not in states:
                states[feed.state] = []
            states[feed.state].append(feed.name)
    
    for state, feeds in sorted(states.items()):
        print(f"  {state}:")
        for feed_name in feeds:
            print(f"    - {feed_name}")
    
    print("\nLGBTIQ+ FEEDS:")
    for feed in get_feeds_by_region(FeedRegion.QUEER):
        print(f"  - {feed.name}")
    
    print("\nREGIONAL FEEDS:")
    for feed in get_feeds_by_region(FeedRegion.REGIONAL):
        print(f"  - {feed.name} ({feed.state})")
    
    print("\n" + "=" * 70)





