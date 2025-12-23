import requests
from datetime import datetime, timedelta
import time
import csv
import os


DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', "https://discord.com/api/webhooks/1453133125751279646/1WXISsYDDzvfMEpDfM8-lVgFuqseiof_TcF-AEvBa770AJE-CT6yOt7arF4325ZYYno4")


ALERT_KEYWORDS = ["hate crime", "lgbtq+", "lgbtiq", "homophobic", "transphobic", "harassment", "assault", "violence", "discriminatory", "bias attack"]


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
        if response.status_code == 204:
            print("✅ Alert sent at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        else:
            print("❌ FAIL - Status: " + str(response.status_code))
            return False
    except Exception as e:
        print("❌ ERROR: " + str(e))
        return False


def check_for_hate_crimes(text_data):
    text_lower = text_data.lower()
    for keyword in ALERT_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False


def scrape_incident_data():
    """
    Read incidents from your existing Incidex CSV files
    Only returns incidents from the last 24 hours
    """
    incidents = []
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    csv_files = [
        'data/incidents-in-progress.csv',
        'data/incidents-news-sourced.csv',
        'data/community-reports.csv'
    ]
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print("⚠️  File not found: " + csv_file)
            continue
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    incident_date = row.get('date') or row.get('dateOfIncident') or row.get('Date') or ''
                    
                    if incident_date and incident_date >= yesterday:
                        description = row.get('description') or row.get('incident_description') or row.get('Description') or ''
                        location = row.get('location') or row.get('suburb') or row.get('Location') or 'Unknown'
                        incident_type = row.get('incidentType') or row.get('incident_type') or row.get('Incident Type') or ''
                        
                        high_severity_types = ['assault', 'violence', 'murder', 'attack', 'harassment']
                        severity = 'high' if any(t in incident_type.lower() for t in high_severity_types) else 'medium'
                        
                        incident = {
                            'description': description,
                            'location': location,
                            'date': incident_date,
                            'source': os.path.basename(csv_file),
                            'severity': severity,
                            'incident_type': incident_type
                        }
                        incidents.append(incident)
        except Exception as e:
            print("⚠️  Error reading " + csv_file + ": " + str(e))
    
    return incidents


def process_incident(incident):
    description = incident.get("description", "")
    if check_for_hate_crimes(description):
        severity = incident.get("severity", "medium").lower()
        if severity not in ["low", "medium", "high", "critical"]:
            severity = "medium"
        
        title = "Hate Crime - " + incident.get('location', 'Unknown')
        alert_description = description[:200] + "..." if len(description) > 200 else description
        
        incident_data = {
            "location": incident.get("location", "Unknown"),
            "date": incident.get("date", "Unknown"),
            "severity": severity,
            "type": incident.get("incident_type", "Not specified"),
            "source": incident.get("source", "Unknown")
        }
        
        send_discord_alert(title=title, description=alert_description, incident_data=incident_data, severity=severity)
        return True
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 HATE CRIME DETECTION SYSTEM STARTED")
    print("=" * 60)
    print("")
    
    print("📂 Reading incidents from CSV files...")
    incidents = scrape_incident_data()
    
    if not incidents:
        print("ℹ️  No new incidents found in the last 24 hours")
    else:
        print("📋 Found " + str(len(incidents)) + " incidents to process")
        print("")
        
        alert_count = 0
        for i, incident in enumerate(incidents, 1):
            print("Processing incident " + str(i) + "/" + str(len(incidents)))
            print("Location: " + incident['location'])
            print("Description: " + incident['description'][:60] + "...")
            
            if process_incident(incident):
                alert_count += 1
                print("✅ ALERT TRIGGERED!")
                time.sleep(0.5)
            else:
                print("ℹ️  No alert needed")
            print("")
        
        print("=" * 60)
        print("✅ Complete. " + str(alert_count) + " alerts sent to Discord")
        print("=" * 60)
