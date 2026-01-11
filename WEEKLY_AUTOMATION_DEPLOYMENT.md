# Weekly Automation Deployment Guide

**Date:** 2025-12-28  
**Status:** ✅ **WORKFLOWS CREATED - READY FOR DEPLOYMENT**

---

## Complete Automation Suite

### Three GitHub Actions Workflows

1. **Daily RSS Monitoring**
   - Schedule: Daily at 2 AM AEDT
   - File: `.github/workflows/daily-rss-monitor.yml`
   - Output: `data/incidents_news_sourced.csv`

2. **Weekly Legal Cases Monitor** ⭐ NEW
   - Schedule: Monday 3 AM AEDT
   - File: `.github/workflows/weekly-legal-cases.yml`
   - Output: `data/legal-cases.csv`

3. **Weekly Parliamentary Monitor** ⭐ NEW
   - Schedule: Tuesday 3 AM AEDT
   - File: `.github/workflows/weekly-parliament-monitor.yml`
   - Output: `data/parliament_activity.csv`

---

## Deployment Steps

### Step 1: Stage Workflows

```bash
git add .github/workflows/weekly-legal-cases.yml
git add .github/workflows/weekly-parliament-monitor.yml
```

### Step 2: Commit

```bash
git commit -m "Add: Weekly legal cases and parliamentary monitors

- Weekly legal cases monitor (Monday 3 AM AEDT)
- Weekly parliamentary monitor (Tuesday 3 AM AEDT)
- Uses existing GOOGLE_API_KEY and OPENAI_API_KEY secrets
- Commits results automatically to CSV files"
```

### Step 3: Push

```bash
git push origin main
```

---

## Verification

### In GitHub Actions Dashboard

Go to: `https://github.com/[your-repo]/actions`

You should see **THREE workflows**:
1. ✅ Daily RSS Monitoring
2. ✅ Weekly Legal Cases Monitor
3. ✅ Weekly Parliamentary Monitor

### Workflow Schedules

| Workflow | Cron | Time (AEDT) | Day |
|----------|------|-------------|-----|
| Daily RSS | `0 16 * * *` | 2 AM | Daily |
| Legal Cases | `0 17 * * 0` | 3 AM | Monday |
| Parliament | `0 17 * * 1` | 3 AM | Tuesday |

---

## Output Files

### Legal Cases
- **File:** `data/legal-cases.csv`
- **Created by:** `scripts/legal_cases_scraper.py`
- **Updated:** Weekly (Monday)

### Parliamentary Activity
- **File:** `data/parliament_activity.csv`
- **Created by:** `scripts/parliament_scraper.py`
- **Updated:** Weekly (Tuesday)

### RSS Incidents
- **File:** `data/incidents_news_sourced.csv`
- **Created by:** `scripts/rss_agent.py`
- **Updated:** Daily

---

## Local Testing (Optional)

### Test Legal Cases Scraper

```bash
cd scripts
python legal_cases_scraper.py
```

Verify:
- No errors
- Creates/updates `data/legal-cases.csv`
- Contains case data

### Test Parliament Scraper

```bash
cd scripts
python parliament_scraper.py
```

Verify:
- No errors
- Creates/updates `data/parliament_activity.csv`
- Contains parliamentary activity data

---

## Integration (Future)

### Update Visualizations

1. **Legal Guides** (`visualizations/legal_guides.html`)
   - Load `data/legal-cases.csv`
   - Display recent cases
   - Link to judgments

2. **Statistics Dashboard** (`visualizations/statistics.html`)
   - Count legal cases
   - Count active bills
   - Display recent votes

3. **Map Visualization**
   - Integrate parliamentary updates
   - Link policy changes to incidents

---

## Status Summary

✅ **COMPLETE AUTOMATION SUITE OPERATIONAL**

**All Components:**
- ✅ Daily RSS monitoring (already deployed)
- ✅ Weekly legal cases monitoring (ready to deploy)
- ✅ Weekly parliamentary monitoring (ready to deploy)
- ✅ All use existing API keys (GitHub Secrets)
- ✅ All commit results automatically
- ✅ All scheduled appropriately

**Next Action:**
Deploy workflows using git commands above.

**The complete automation suite is ready! 🚀**





