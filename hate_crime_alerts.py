import requests
from datetime import datetime, timedelta
import csv
import os

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', "https://discord.com/api/webhooks/1453133125751279646/1WXISsYDDzvfMEpDfM8-lVgFuqseiof_TcF-AEvBa770AJE-CT6yOt7arF4325ZYYno4")

ALERT_KEYWORDS = ["hate crime", "lgbtq+", "lgbtiq", "homophobic", "transphobic", "harassment", "assault", "violence"]

def send_discord_alert(title, description, incident_data=None, severity="medium"):
    severity_colors = {"low": 65280, "medium": 16776960, "high": 16711680, "critical": 10040064}
    color = severity_colors.get(severity, 16776960)
    payload = {
        "content": "🚨 **" + severity.upper() + " PRIORITY** - Hate Crime Incident Detected",
        "embeds": [{"title": title, "description": description, "color": color, "timestamp": datetime.utcnow().isoformat(), "fields": []}]
    }
    if incident_data:
        for key, value in incident_data.items():
            payload["embeds"][0]["fields"].append({"name": key.replace("_", " ").title(), "value": str(value), "inline": False})
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})
        return response.status_code == 204
    except Exception as e:
        print("ERROR: " + str(e))
        return False

def check_for_hate_crimes(text_data):
    return any(keyword.lower() in text_data.lower() for keyword in ALERT_KEYWORDS)

def scrape_incident_data():
    incidents = []
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    csv_files = ['data/incidents-in-progress.csv', 'data/incidents-news-sourced.csv', 'data/community-reports.csv']
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    incident_date = row.get('date') or row.get('dateOfIncident') or ''
                    if incident_date and incident_date >= yesterday:
                        incidents.append({
                            'description': row.get('description') or '',
                            'location': row.get('location') or 'Unknown',
                            'date': incident_date,
                            'severity': 'high' if any(t in (row.get('incidentType') or '').lower() for t in ['assault', 'violence', 'murder']) else 'medium'
                        })
        except:
            pass
    return incidents

if __name__ == "__main__":
    incidents = scrape_incident_data()
    alert_count = 0
    for incident in incidents:
        if check_for_hate_crimes(incident['description']):
            send_discord_alert(
                title="Hate Crime - " + incident['location'],
                description=incident['description'][:200],
                incident_data={"location": incident['location'], "date": incident['date'], "severity": incident['severity']},
                severity=incident['severity']
            )
            alert_count += 1
    print("Complete. " + str(alert_count) + " alerts sent")
