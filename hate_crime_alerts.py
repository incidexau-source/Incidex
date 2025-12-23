import requests
from datetime import datetime
import time

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1453133125751279646/1WXISsYDDzvfMEpDfM8-lVgFuqseiof_TcF-AEvBa770AJE-CT6yOt7arF4325ZYYno4"

ALERT_KEYWORDS = ["hate crime", "lgbtq+", "lgbtiq", "homophobic", "transphobic", "harassment", "assault", "violence", "discriminatory", "bias attack"]

def send_discord_alert(title, description, incident_data=None, severity="medium"):
    severity_colors = {"low": 65280, "medium": 16776960, "high": 16711680, "critical": 10040064}
    color = severity_colors.get(severity, 16776960)
    
    payload = {
        "content": "ALERT - " + severity.upper() + " PRIORITY",
        "embeds": [{"title": title, "description": description, "color": color, "timestamp": datetime.utcnow().isoformat(), "fields": []}]
    }
    
    if incident_data:
        for key, value in incident_data.items():
            payload["embeds"][0]["fields"].append({"name": key.replace("_", " ").title(), "value": str(value), "inline": False})
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 204:
            print("OK - Alert sent at " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return True
        else:
            print("FAIL - Status: " + str(response.status_code))
            return False
    except Exception as e:
        print("ERROR: " + str(e))
        return False

def check_for_hate_crimes(text_data):
    text_lower = text_data.lower()
    for keyword in ALERT_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def process_incident(incident):
    description = incident.get("description", "")
    if check_for_hate_crimes(description):
        severity = incident.get("severity", "medium").lower()
        if severity not in ["low", "medium", "high", "critical"]:
            severity = "medium"
        
        title = "Hate Crime - " + incident.get('location', 'Unknown')
        alert_description = description[:200] + "..." if len(description) > 200 else description
        
        send_discord_alert(title=title, description=alert_description, incident_data={"location": incident.get("location", "Unknown"), "date": incident.get("date", "Unknown"), "severity": severity, "category": incident.get("category", "Not specified")}, severity=severity)
        return True
    return False

if __name__ == "__main__":
    print("HATE CRIME DETECTION SYSTEM STARTED")
    print("=" * 50)
    
    test_incidents = [
        {"description": "LGBTQ+ individual assaulted at downtown area", "location": "Melbourne CBD", "date": "2025-12-24", "severity": "high", "category": "Physical Assault"},
        {"description": "Homophobic graffiti found on community center", "location": "Armadale Station", "date": "2025-12-24", "severity": "low", "category": "Vandalism"},
        {"description": "Regular theft incident at store", "location": "Local Shop", "date": "2025-12-24", "severity": "low", "category": "Theft"},
        {"description": "Transphobic harassment incident on public transport", "location": "Tram Line 48", "date": "2025-12-24", "severity": "medium", "category": "Harassment"}
    ]
    
    alert_count = 0
    for i, incident in enumerate(test_incidents, 1):
        print("")
        print("Processing incident " + str(i) + "/" + str(len(test_incidents)))
        print("Location: " + incident['location'])
        print("Description: " + incident['description'][:50] + "...")
        
        if process_incident(incident):
            alert_count += 1
            print("ALERT TRIGGERED!")
            time.sleep(1)
        else:
            print("No alert needed")
    
    print("")
    print("=" * 50)
    print("Complete. " + str(alert_count) + " alerts sent to Discord")
