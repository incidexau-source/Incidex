from datetime import datetime, timedelta
import csv
import os

ALERT_KEYWORDS = ["hate crime", "lgbtq+", "lgbtiq", "homophobic", "transphobic", "harassment", "assault", "violence"]

LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'alerts.log')


def log_alert(title, description, incident_data=None, severity="medium"):
    """Write alert to log file instead of sending to Discord."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{severity.upper()}] {title}\n")
        f.write(f"  Description: {description}\n")
        if incident_data:
            for key, value in incident_data.items():
                f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
        f.write("\n")
    print(f"[{severity.upper()}] {title}")


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
        except Exception:
            pass
    return incidents


if __name__ == "__main__":
    incidents = scrape_incident_data()
    alert_count = 0
    for incident in incidents:
        if check_for_hate_crimes(incident['description']):
            log_alert(
                title="Hate Crime - " + incident['location'],
                description=incident['description'][:200],
                incident_data={"location": incident['location'], "date": incident['date'], "severity": incident['severity']},
                severity=incident['severity']
            )
            alert_count += 1
    print("Complete. " + str(alert_count) + " new incidents logged.")
