
import os
import sys
import feedparser
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rss_feeds import get_all_feeds

# Setup validation logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugRSS")

def debug_feeds():
    feeds = get_all_feeds()
    print(f"Loaded {len(feeds)} feeds.")
    
    total_articles = 0
    total_content_length = 0
    
    for feed_config in feeds:
        print(f"\nChecking feed: {feed_config.name} ({feed_config.url})")
        try:
            feed = feedparser.parse(feed_config.url)
            if not feed.entries:
                print("  [!] No entries found in feed.")
                if feed.bozo:
                     print(f"  [!] Feed Bozo Exception: {feed.bozo_exception}")
                continue
                
            print(f"  Found {len(feed.entries)} entries. Inspecting first 3...")
            
            for i, entry in enumerate(feed.entries[:3]):
                title = entry.title
                link = entry.link
                content = entry.get('summary', '') or entry.get('description', '')
                if 'content' in entry:
                    content += " " + " ".join([c.value for c in entry.content])
                
                print(f"  [{i+1}] Title: {title}")
                print(f"      Link: {link}")
                print(f"      Content Length: {len(content)}")
                print(f"      Snippet: {content[:100]}...")
                
                total_articles += 1
                total_content_length += len(content)
                
        except Exception as e:
            print(f"  [!] Error parsing feed: {e}")

    print(f"\nDone. Processed {total_articles} articles.")

if __name__ == "__main__":
    debug_feeds()
