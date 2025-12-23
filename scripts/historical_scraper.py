import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

def fetch_gdelt_by_month(year, month):
    """Fetch GDELT news for a specific month"""
    
    # First day of month
    start_date = datetime(year, month, 1)
    
    # Last day of month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    start = start_date.strftime('%Y%m%d000000')
    end = end_date.strftime('%Y%m%d235959')
    
    # Search query
    query = '(LGBT OR LGBTIQ OR gay OR lesbian OR transgender OR queer OR homophobic OR transphobic) AND (attack OR assault OR violence OR hate OR discrimination) AND Australia'
    
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    
    params = {
        'query': query,
        'mode': 'artlist',
        'maxrecords': 250,
        'format': 'json',
        'startdatetime': start,
        'enddatetime': end
    }
    
    try:
        print(f"  Fetching {start_date.strftime('%B %Y')}...", end=" ", flush=True)
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        articles = data.get('articles', [])
        print(f"Found {len(articles)} articles")
        
        return articles
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def collect_historical_data(start_year=2020, end_year=2025):
    """Collect data from 5 years back"""
    
    all_articles = []
    total_months = (end_year - start_year + 1) * 12
    current_month = 0
    
    print(f"\nCollecting historical data from {start_year} to {end_year}...")
    print(f"This will take 10-15 minutes. Please wait...\n")
    
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            current_month += 1
            articles = fetch_gdelt_by_month(year, month)
            all_articles.extend(articles)
            
            # Be respectful to the API - add delay between requests
            time.sleep(2)
            
            # Progress indicator
            print(f"  Progress: {current_month}/{total_months} months")
    
    print(f"\nTotal articles found: {len(all_articles)}")
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'seendate': article.get('seendate', ''),
            'source': article.get('source', ''),
            'article_text': article.get('text', '') if 'text' in article else article.get('title', '')
        }
        for article in all_articles
    ])
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/raw_articles.csv', index=False)
    print(f"\nSaved {len(df)} articles to data/raw_articles.csv")
    
    return df

if __name__ == "__main__":
    print("=" * 60)
    print("LGBTIQ+ HATE CRIME HISTORICAL DATA COLLECTION")
    print("=" * 60)
    
    df = collect_historical_data(start_year=2020, end_year=2025)
    print("\nHistorical collection complete!")
    print(f"You now have {len(df)} articles to process.")

