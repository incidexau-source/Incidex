"""
Test Script for Gemini Accuracy
Runs 50 sample articles through the Gemini filter and extractor to verify performance.
"""

import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts import gemini_extractor

# Sample Data (Mixed relevant and irrelevant)
# 20 Relevant (LGBTIQ+ Hate Crimes in Australia)
# 30 Irrelevant (General news, overseas incidents, positive stories)

SAMPLE_ARTICLES = [
    # RELEVANT (Actual or Realistic Hate Crimes)
    {"id": 1, "expected": True, "title": "Gay couple bashed on Oxford Street", "text": "Two men were hospitalized after a homophobic assault on Oxford Street, Sydney."},
    {"id": 2, "expected": True, "title": "Trans woman harassed on train in Melbourne", "text": "Police are investigating after a trans woman was verbally abused and threatened on a train to Flinders Street."},
    {"id": 3, "expected": True, "title": "Vandals paint swastikas on Jewish and LGBT centre", "text": "A community centre in St Kilda hosting an LGBT event was defaced with Nazi symbols."},
    {"id": 4, "expected": True, "title": "Man charged over hate crime in Brisbane", "text": "A 40-year-old man has been charged with assault after attacking a drag queen at a library reading event."},
    {"id": 5, "expected": True, "title": "Homophobic slur shouted before punch thrown", "text": "A Perth man suffered facial injuries after being punched by a stranger who used a homophobic slur."},
    {"id": 6, "expected": True, "title": "Lesbian couple targeted in home invasion", "text": "Adelaide police suspect a home invasion was a targeted hate crime against a lesbian couple."},
    {"id": 7, "expected": True, "title": "Trans teen bullied and beaten at school", "text": "A transgender student in Western Sydney was hospitalised after a brutal schoolyard attack."},
    {"id": 8, "expected": True, "title": "Pride flag burned outside council chambers", "text": "Vandals set fire to a Pride flag flying outside the local council building in regional Victoria."},
    {"id": 9, "expected": True, "title": " Drag Story Time protestors clash with police", "text": "Protestors shouting anti-LGBT slogans clashed with police and attendees at a Melbourne library."},
    {"id": 10, "expected": True, "title": "Man fined for offensive behavior towards gay couple", "text": "A man has been fined for threatening a gay couple holding hands in a shopping centre."},
    {"id": 11, "expected": True, "title": "Murder investigation: Gay man found dead in park", "text": "Homicide detectives are investigating the suspicious death of a gay man in a known beat in Sydney."},
    {"id": 12, "expected": True, "title": "Anti-trans stickers plastered over Newtown", "text": "Residents are angry after anti-trans stickers were found covering poles and signs in Newtown."},
    {"id": 13, "expected": True, "title": "Dating app robbery gang sentences", "text": "Three men who lured gay men via Grindr to rob and assault them have been sentenced."},
    {"id": 14, "expected": True, "title": "Religious discrimination bill debate heats up after attack", "text": "Debate intensifies after a student was expelled and harassed for being gay."},
    {"id": 15, "expected": True, "title": "Queer space windows smashed in Hobart", "text": "Police are reviewing CCTV after windows were smashed at a popular queer venue in Hobart."},
    {"id": 16, "expected": True, "title": "Online threats made against trans activist", "text": "Police are investigating death threats sent to a prominent Australian trans activist."},
    {"id": 17, "expected": True, "title": "Petrol poured on doorstep of same-sex couple", "text": "A terrifying incident where petrol was poured on the doorstep of a same-sex couple's home."},
    {"id": 18, "expected": True, "title": "Bi man assaulted leaving Mardi Gras aftermath", "text": "A bisexual man was assaulted while walking home from Mardi Gras celebrations."},
    {"id": 19, "expected": True, "title": "Vote No skywriter pilot makes homophobic remarks", "text": "Controversy erupts after a pilot writes homophobic slurs in the sky over Sydney."},
    {"id": 20, "expected": True, "title": "Church sign vandalised with 'Love is Love'", "text": "Actually, this is vandalism, but is it a hate crime AGAINST LGBTIQ? Usually 'Love is Love' is pro-LGBTIQ. Let's see if Gemini excludes it or includes it as related incident. It's technically vandalism. But usually we track hate crimes *against* the community. Expected: False (or tricky). Let's set expected to False for 'hate crime against LGBTIQ'."},

    # IRRELEVANT (General News, Overseas, Positive)
    {"id": 21, "expected": False, "title": "Prime Minister announces new tax cuts", "text": "The PM announced tax cuts for middle income earners today."},
    {"id": 22, "expected": False, "title": "Sydney Mardi Gras parade a huge success", "text": "Thousands turned out for a peaceful and joyous Mardi Gras parade on Oxford Street."},
    {"id": 23, "expected": False, "title": "US hate crimes rise in 2024", "text": "FBI data shows a rise in anti-LGBT hate crimes across the United States. (Overseas)"},
    {"id": 24, "expected": False, "title": "New cafe opens in Darlinghurst", "text": "A new trendy cafe has opened in the heart of the gay district."},
    {"id": 25, "expected": False, "title": "Weather forecast: Rain expected for Sydney", "text": "Heavy rain is forecast for the east coast this weekend."},
    {"id": 26, "expected": False, "title": "Man charged with bank robbery", "text": "Police have arrested a man in relation to a bank robbery in Parramatta."},
    {"id": 27, "expected": False, "title": "UK Parliament debates trans rights", "text": "Debate in Westminster regarding gender recognition certificates. (Overseas)"},
    {"id": 28, "expected": False, "title": "Footballer comes out as gay", "text": "A professional AFL player has come out as gay, receiving overwhelming support."},
    {"id": 29, "expected": False, "title": "Car crash on M1 causes delays", "text": "A multi-vehicle crash has caused peak hour chaos."},
    {"id": 30, "expected": False, "title": "Local council approves new park", "text": "Council has voted to build a new playground in the inner west."},
    {"id": 31, "expected": False, "title": "Uganda passes strict anti-gay laws", "text": "International condemnation as Uganda tightens laws. (Overseas)"},
    {"id": 32, "expected": False, "title": "Russian court bans LGBT movement", "text": "Russia has declared the international LGBT movement extremist. (Overseas)"},
    {"id": 33, "expected": False, "title": "Teacher strike planned for Friday", "text": "Teachers union announces industrial action over pay."},
    {"id": 34, "expected": False, "title": "New research on HIV treatment", "text": "Australian scientists make breakthrough in HIV research."},
    {"id": 35, "expected": False, "title": "Qantas posts record profit", "text": "The national carrier has announced a profit turnaround."},
    {"id": 36, "expected": False, "title": "Melbourne property prices fall", "text": "Housing market cools in Victoria."},
    {"id": 37, "expected": False, "title": "Man rescues dog from floodwaters", "text": "Heroic rescue of a dog caught in rising floodwaters."},
    {"id": 38, "expected": False, "title": "Review: New queer cinema festival", "text": "A review of the latest films at the Queer Film Festival. (Positive/Arts)"},
    {"id": 39, "expected": False, "title": "Opinion: Why we need marriage equality", "text": "An opinion piece reflecting on the anniversary of marriage equality."},
    {"id": 40, "expected": False, "title": "Police investigate burglary in Toorak", "text": "Jewellery and cash stolen from a luxury home."},
    # ... filling up to 50 with generic irrelevant
    {"id": 41, "expected": False, "title": "Stock market update", "text": "ASX 200 closes higher."},
    {"id": 42, "expected": False, "title": "New iPhone released", "text": "Apple announces latest model."},
    {"id": 43, "expected": False, "title": "Cricket: Australia wins the Ashes", "text": "Victory at the MCG."},
    {"id": 44, "expected": False, "title": "Hospital waiting times increase", "text": "Patients waiting longer for emergency care."},
    {"id": 45, "expected": False, "title": "Bus driver strike", "text": "Commuters warned of delays."},
    {"id": 46, "expected": False, "title": "Shark sighting at Bondi", "text": "Swimmers evacuated from water."},
    {"id": 47, "expected": False, "title": "New corruption Inquiry", "text": "ICAC announces new public hearings into developer deals."},
    {"id": 48, "expected": False, "title": "Fashion Week highlights", "text": "Designers showcase new collections."},
    {"id": 49, "expected": False, "title": "Best restaurants in Sydney", "text": "Top 10 dining spots revealed."},
    {"id": 50, "expected": False, "title": "Gardening tips for spring", "text": "How to prune your roses."},
]

def run_test():
    print(f"Running Gemini Accuracy Test on {len(SAMPLE_ARTICLES)} articles...")
    print("-" * 60)
    
    correct = 0
    false_positives = 0
    false_negatives = 0
    start_time = time.time()
    
    results = []
    
    for article in SAMPLE_ARTICLES:
        print(f"Testing ID {article['id']}: {article['title']}...", end=" ", flush=True)
        try:
            prediction = gemini_extractor.filter_article(article['title'], article['text'])
            
            # Special case for ID 20: if prediction is False (it's not a hate crime AGAINST LGBT), 
            # but we marked expected as False, it aligns.
            
            is_correct = (prediction == article['expected'])
            
            if is_correct:
                print("PASS")
                correct += 1
            else:
                print(f"FAIL (Expected {article['expected']}, Got {prediction})")
                if prediction:
                    false_positives += 1
                else:
                    false_negatives += 1
            
            results.append({
                "id": article['id'],
                "title": article['title'],
                "expected": article['expected'],
                "predicted": prediction,
                "status": "PASS" if is_correct else "FAIL"
            })
            
            # Rate limit handling (free tier)
            time.sleep(1) 
            
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"id": article['id'], "status": "ERROR", "error": str(e)})
            
    end_time = time.time()
    duration = end_time - start_time
    
    accuracy = (correct / len(SAMPLE_ARTICLES)) * 100
    
    print("-" * 60)
    print(f"Test Complete in {duration:.2f} seconds")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Correct: {correct}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")
    print("-" * 60)
    
    # Generate Report Content
    report_content = f"""
# Test Report: Gemini RSS Agent Accuracy
**Date**: {time.strftime("%Y-%m-%d")}
**Model**: gemini-2.0-flash-exp (or default configured)

## Summary
- **Total Articles Tested**: {len(SAMPLE_ARTICLES)}
- **Accuracy**: {accuracy:.1f}%
- **False Positives**: {false_positives}
- **False Negatives**: {false_negatives}
- **Time Taken**: {duration:.2f} seconds

## Detailed Results
| ID | Title | Expected | Predicted | Status |
|----|-------|----------|-----------|--------|
"""
    for r in results:
        report_content += f"| {r.get('id')} | {r.get('title')} | {r.get('expected')} | {r.get('predicted')} | {r.get('status')} |\n"
        
    with open("TEST_REPORT.md", "w") as f:
        f.write(report_content)
    print("Report saved to TEST_REPORT.md")

if __name__ == "__main__":
    run_test()
