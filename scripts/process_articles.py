import pandas as pd
import json
import time
from openai import OpenAI
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, RATE_LIMIT_DELAY

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_incident_data(article_title, article_text):
    # Handle None, NaN, or non-string article text
    if not isinstance(article_text, str):
        article_text = str(article_title) if isinstance(article_title, str) else ""
    
    # Handle None or non-string titles
    if not isinstance(article_title, str):
        article_title = ""
    
    prompt = f"Analyze this Australian news article about LGBTIQ+ issues.\n\n"
    prompt += f"If this article describes an ACTUAL hate crime incident (physical attack, assault, harassment, vandalism, hate speech targeting LGBTIQ+ person), extract details. If it's just general news about LGBTIQ+ issues, discrimination debates, or policy discussions, return null.\n\n"
    prompt += f"Article Title: {article_title}\n"
    prompt += f"Article Text: {article_text[:1000]}\n\n"
    prompt += f"CRITICAL: For location, extract the MOST SPECIFIC location mentioned in the article. Priority order:\n"
    prompt += f"1. Street name and suburb (e.g., 'Oxford Street, Darlinghurst' or 'Smith Street, Collingwood')\n"
    prompt += f"2. Suburb/neighborhood name (e.g., 'Newtown', 'Fitzroy', 'Surfers Paradise')\n"
    prompt += f"3. Specific venue/landmark (e.g., 'Sydney Opera House', 'Melbourne Central Station')\n"
    prompt += f"4. Only if none of the above are mentioned, use city name (e.g., 'Sydney', 'Melbourne')\n"
    prompt += f"NEVER use generic terms like 'not specified', 'Australia', or leave it blank. Always extract the most specific location available.\n\n"
    prompt += f"Return ONLY valid JSON (no markdown, no explanation):\n"
    prompt += f'{{"is_hate_crime": true/false, "incident_type": "assault|harassment|vandalism|hate_speech|threat|other", "date": "YYYY-MM-DD or null", "location": "MOST SPECIFIC location: street+suburb > suburb > venue > city (never generic terms)", "victim_identity": "gay|lesbian|transgender|bisexual|queer|general_lgbtiq|unknown", "description": "2-3 sentence summary", "severity": "low|medium|high", "perpetrator_info": "brief description if mentioned, else null"}}\n\n'
    prompt += f'If NOT a hate crime incident, return: {{"is_hate_crime": false}}'

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("json"):
            result_text = result_text[4:]
        
        result = json.loads(result_text)
        return result
        
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return {"is_hate_crime": False}
    except Exception as e:
        print(f"  API error: {e}")
        return {"is_hate_crime": False}

print("=" * 60)
print("PROCESSING ARTICLES WITH AI")
print("=" * 60)

try:
    df = pd.read_csv('data/raw_articles.csv')
    print(f"\nLoaded {len(df)} raw articles")
except FileNotFoundError:
    print("Error: data/raw_articles.csv not found. Run historical_scraper.py first.")
    sys.exit(1)

df = df.drop_duplicates(subset=['url'])
print(f"After removing duplicates: {len(df)} articles")

# Load existing progress if it exists
incidents = []
processed_urls = set()

if os.path.exists('data/incidents_in_progress.csv'):
    try:
        progress_df = pd.read_csv('data/incidents_in_progress.csv')
        if len(progress_df) > 0:
            print("\nFound previous progress file. Resuming...")
            incidents = progress_df.to_dict('records')
            processed_urls = set(progress_df['url'].values)
            print(f"Already found {len(incidents)} hate crime incidents")
            print(f"Already processed {len(processed_urls)} URLs total")
    except:
        print("\nStarting fresh...")

# Load processed URLs file (tracks ALL processed, not just hate crimes)
if os.path.exists('data/processed_urls.txt'):
    with open('data/processed_urls.txt', 'r') as f:
        processed_urls = set(line.strip() for line in f)
    print(f"Loaded {len(processed_urls)} previously processed URLs")

total = len(df)

print(f"\nProcessing articles (this will take 1-2 hours)...")
print("You can stop anytime with Ctrl+C and resume later.\n")

for idx, row in df.iterrows():
    # Skip if already processed
    if row['url'] in processed_urls:
        continue
        
    print(f"[{idx+1}/{total}] Processing...", end=" ", flush=True)
    
    article_text = row.get('article_text', row.get('title', ''))
    result = extract_incident_data(row['title'], article_text)
    
    # Handle None result
    if result is None:
        result = {"is_hate_crime": False}
    
    if result.get('is_hate_crime', False):
        incident = {
            'title': row['title'],
            'url': row['url'],
            'source_date': row['seendate'],
            'incident_type': result.get('incident_type'),
            'date': result.get('date'),
            'location': result.get('location'),
            'victim_identity': result.get('victim_identity'),
            'description': result.get('description'),
            'severity': result.get('severity'),
            'perpetrator_info': result.get('perpetrator_info')
        }
        incidents.append(incident)
        print(f"[HATE CRIME] Found ({len(incidents)} total)")
    else:
        print("[SKIP] Not a hate crime")
    
    processed_urls.add(row['url'])
    
    time.sleep(RATE_LIMIT_DELAY)
    
    if len(processed_urls) % 100 == 0:
        # Save incidents
        incidents_df = pd.DataFrame(incidents)
        incidents_df.to_csv('data/incidents_in_progress.csv', index=False)
        # Save all processed URLs
        with open('data/processed_urls.txt', 'w') as f:
            for url in processed_urls:
                f.write(url + '\n')
        print(f"\n  -> Progress saved: {len(incidents)} incidents, {len(processed_urls)} URLs processed\n")

# Final save
incidents_df = pd.DataFrame(incidents)
incidents_df.to_csv('data/incidents_extracted.csv', index=False)
with open('data/processed_urls.txt', 'w') as f:
    for url in processed_urls:
        f.write(url + '\n')

print("\n" + "=" * 60)
print(f"PROCESSING COMPLETE!")
print(f"Found {len(incidents)} hate crime incidents out of {total} articles")
print(f"Processed {len(processed_urls)} URLs total")
print(f"Saved to: data/incidents_extracted.csv")
print("=" * 60)