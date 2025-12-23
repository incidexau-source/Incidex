"""
Master Execution Script for Historical Scraping (2005-2019)
Orchestrates the complete historical data scraping operation.
"""

import os
import sys
import logging
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from scripts.historical_scraper_2005_2019 import HistoricalScraper2005_2019

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "logs" / f"historical_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
FINAL_REPORT_JSON = DATA_DIR / "historical_scraping_complete_report.json"


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Execute Historical Scraping for 2005-2019"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving files (for testing)"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("=" * 70)
        logger.info("HISTORICAL DATA SCRAPING: 2005-2019")
        logger.info("=" * 70)
        logger.info(f"Execution started: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 70)
        
        scraper = HistoricalScraper2005_2019(dry_run=args.dry_run)
        result = scraper.run()
        
        # Save final report
        if not args.dry_run:
            with open(FINAL_REPORT_JSON, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"\nFinal report saved to {FINAL_REPORT_JSON}")
        
        # Print summary
        print("\n" + "=" * 70)
        print("HISTORICAL SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Unique incidents found: {result['summary']['unique_incidents']}")
        print(f"Total searches executed: {result['summary']['searches_executed']}")
        print(f"Articles found: {result['summary']['articles_found']}")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

