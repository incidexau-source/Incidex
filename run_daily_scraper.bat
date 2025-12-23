@echo off
setlocal
cd /d C:\Users\Tom\OneDrive\Desktop\lgbtiq-hate-crime-map
if not exist logs mkdir logs
python scripts\daily_scraper.py >> logs\daily_scraper.log 2>&1
endlocal

