"""
Article Fetcher for RSS Feed Monitoring

This module handles fetching RSS feeds, parsing entries, and extracting
full article text from URLs. Includes retry logic, user-agent rotation,
and error handling for robust operation in automated environments.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional, Iterator
from dataclasses import dataclass
import requests
import feedparser
from newspaper import Article
from trafilatura import fetch_url, extract


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ArticleData:
    """
    Structured article data extracted from RSS feeds
    
    Attributes:
        title: Article headline
        url: Full article URL
        publication_date: When the article was published (from RSS feed)
        summary: RSS feed snippet/summary (may be truncated)
        full_text: Full article body text (after downloading)
        source_name: Name of the news source (for attribution)
        feed_url: Original RSS feed URL
    """
    title: str
    url: str
    publication_date: datetime
    summary: Optional[str] = None
    full_text: Optional[str] = None
    source_name: Optional[str] = None
    feed_url: Optional[str] = None


# User agents for rotation (prevents blocking)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class ArticleFetcher:
    """
    Handles fetching and parsing of articles from RSS feeds.
    
    Features:
    - RSS/Atom feed parsing with feedparser
    - Full article text extraction using newspaper3k and trafilatura
    - Retry logic for network failures
    - User-agent rotation
    - Rate limiting respect
    """
    
    def __init__(
        self,
        request_timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
        rate_limit_delay: float = 1.0,
        use_newspaper: bool = True,
    ):
        """
        Initialize the ArticleFetcher.
        
        Args:
            request_timeout: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Delay between retries in seconds
            rate_limit_delay: Minimum delay between requests (rate limiting)
            use_newspaper: If True, use newspaper3k; else use trafilatura
        """
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit_delay = rate_limit_delay
        self.use_newspaper = use_newspaper
        self._user_agent_index = 0
    
    def _get_user_agent(self) -> str:
        """Rotate through user agents to avoid detection."""
        agent = USER_AGENTS[self._user_agent_index]
        self._user_agent_index = (self._user_agent_index + 1) % len(USER_AGENTS)
        return agent
    
    def _make_request(self, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic and user-agent rotation.
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            requests.Response object
            
        Raises:
            requests.RequestException: If all retries fail
        """
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self._get_user_agent()
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url,
                    timeout=self.request_timeout,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")
                    raise
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed for {url}: {e}")
                time.sleep(self.retry_delay * attempt)  # Exponential backoff
    
    def fetch_rss_feed(self, feed_url: str, source_name: Optional[str] = None) -> list[ArticleData]:
        """
        Fetch and parse an RSS/Atom feed.
        
        Args:
            feed_url: URL of the RSS/Atom feed
            source_name: Optional name of the news source
            
        Returns:
            List of ArticleData objects (may be empty if feed is inaccessible)
        """
        logger.info(f"Fetching RSS feed: {feed_url}")
        
        try:
            response = self._make_request(feed_url)
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except (ValueError, TypeError):
                        pass
                
                # Fallback to updated_parsed or current time
                if not pub_date:
                    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        try:
                            pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                        except (ValueError, TypeError):
                            pass
                
                if not pub_date:
                    pub_date = datetime.now(timezone.utc)
                
                # Extract article URL
                url = entry.get('link') or entry.get('id')
                if not url:
                    logger.warning(f"Skipping entry without URL: {entry.get('title', 'Untitled')}")
                    continue
                
                article = ArticleData(
                    title=entry.get('title', 'Untitled'),
                    url=url,
                    publication_date=pub_date,
                    summary=entry.get('summary') or entry.get('description'),
                    source_name=source_name,
                    feed_url=feed_url,
                )
                
                articles.append(article)
            
            logger.info(f"Parsed {len(articles)} articles from {feed_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []
        
        finally:
            # Respect rate limiting
            time.sleep(self.rate_limit_delay)
    
    def extract_article_text(self, article: ArticleData) -> ArticleData:
        """
        Download and extract full article text from URL.
        
        Tries newspaper3k first (if enabled), then falls back to trafilatura.
        Updates article.full_text in place.
        
        Args:
            article: ArticleData object with URL set
            
        Returns:
            Updated ArticleData object with full_text populated
        """
        if not article.url:
            logger.warning(f"No URL provided for article: {article.title}")
            return article
        
        logger.debug(f"Extracting text from: {article.url}")
        
        # Try newspaper3k first (if enabled)
        if self.use_newspaper:
            try:
                news_article = Article(article.url)
                news_article.download()
                news_article.parse()
                
                if news_article.text and len(news_article.text.strip()) > 100:
                    article.full_text = news_article.text.strip()
                    logger.debug(f"Extracted {len(article.full_text)} chars using newspaper3k")
                    return article
            except Exception as e:
                logger.debug(f"Newspaper3k extraction failed: {e}, trying trafilatura")
        
        # Fallback to trafilatura
        try:
            downloaded = fetch_url(article.url)
            if downloaded:
                extracted = extract(downloaded, include_comments=False, include_tables=False)
                if extracted and len(extracted.strip()) > 100:
                    article.full_text = extracted.strip()
                    logger.debug(f"Extracted {len(article.full_text)} chars using trafilatura")
                    return article
        except Exception as e:
            logger.warning(f"Trafilatura extraction failed for {article.url}: {e}")
        
        # If both fail, use summary if available
        if article.summary and len(article.summary.strip()) > 100:
            article.full_text = article.summary.strip()
            logger.warning(f"Using RSS summary as fallback for {article.url}")
        else:
            article.full_text = None
            logger.warning(f"Could not extract article text from {article.url}")
        
        return article
    
    def fetch_and_extract_all(
        self,
        feed_url: str,
        source_name: Optional[str] = None,
        extract_full_text: bool = True,
        max_articles: Optional[int] = None,
    ) -> Iterator[ArticleData]:
        """
        Fetch RSS feed and optionally extract full text for each article.
        
        Args:
            feed_url: RSS feed URL
            source_name: Optional source name
            extract_full_text: Whether to download and extract full article text
            max_articles: Limit number of articles to process (None = all)
            
        Yields:
            ArticleData objects
        """
        articles = self.fetch_rss_feed(feed_url, source_name)
        
        if max_articles:
            articles = articles[:max_articles]
        
        for article in articles:
            if extract_full_text:
                article = self.extract_article_text(article)
            yield article
            
            # Rate limiting between articles
            time.sleep(self.rate_limit_delay)
    
    def filter_recent_articles(
        self,
        articles: list[ArticleData],
        hours_back: int = 24
    ) -> list[ArticleData]:
        """
        Filter articles to only those published within the last N hours.
        
        Args:
            articles: List of ArticleData objects
            hours_back: Number of hours to look back (default: 24)
            
        Returns:
            Filtered list of ArticleData objects
        """
        cutoff = datetime.now(timezone.utc).timestamp() - (hours_back * 3600)
        
        filtered = []
        for article in articles:
            if article.publication_date.timestamp() >= cutoff:
                filtered.append(article)
        
        logger.info(f"Filtered {len(articles)} articles to {len(filtered)} from last {hours_back} hours")
        return filtered


# Convenience function for simple use cases
def fetch_articles_from_feed(
    feed_url: str,
    source_name: Optional[str] = None,
    hours_back: int = 24,
    extract_full_text: bool = True,
) -> list[ArticleData]:
    """
    Simple function to fetch articles from a single RSS feed.
    
    Args:
        feed_url: RSS feed URL
        source_name: Optional source name
        hours_back: Only fetch articles from last N hours
        extract_full_text: Whether to extract full article text
        
    Returns:
        List of ArticleData objects
    """
    fetcher = ArticleFetcher()
    articles = list(fetcher.fetch_and_extract_all(feed_url, source_name, extract_full_text))
    
    if hours_back:
        articles = fetcher.filter_recent_articles(articles, hours_back)
    
    return articles


if __name__ == "__main__":
    # Quick test
    import sys
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = "https://www.abc.net.au/news/feed/45910/rss.xml"
    
    print(f"Testing article fetcher with: {test_url}")
    fetcher = ArticleFetcher()
    articles = fetcher.fetch_rss_feed(test_url, "Test Source")
    
    print(f"\nFetched {len(articles)} articles:")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article.title}")
        print(f"   URL: {article.url}")
        print(f"   Date: {article.publication_date}")
        if article.summary:
            print(f"   Summary: {article.summary[:100]}...")





