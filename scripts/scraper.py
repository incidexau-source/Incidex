import requests
from datetime import datetime, timedelta

def fetch_gdelt_news():
    """Fetch LGBTIQ+ hate crime news from GDELT"""
    
    # Set date range (yesterday to today)
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d%H%M%S')
    today = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Search query for LGBTIQ+ hate crimes
    query = '("hate crime" OR "homophobic attack" OR "transphobic" OR "anti-gay" OR "anti-LGBT") AND Australia'
    
    # GDELT API endpoint
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    params = {
        'query': query,
        'mode': 'artlist',
        'maxrecords': 50,
        'format': 'json',
        'startdatetime': yesterday,
        'enddatetime': today
    }
    
    try:
        print(f"Fetching news from {yesterday} to {today}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        
        print(f"Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

# Test the function
if __name__ == "__main__":
    articles = fetch_gdelt_news()
    
    # Print first 3 article titles to verify it works
    for i, article in enumerate(articles[:3], 1):
        print(f"\n{i}. {article.get('title', 'No title')}")
        print(f"   URL: {article.get('url', 'No URL')}")

