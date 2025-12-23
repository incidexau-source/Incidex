"""
Master Execution Script for Section 1
Executes Section 1.1 (Incident Scraper) and Section 1.2 (Verification)

This script orchestrates:
1. Enhanced scraper execution for Nov 1 - Dec 22, 2025
2. Human review alert generation
3. Automation pipeline verification
4. Comprehensive status report generation
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Import scripts
from scripts.enhanced_nov_dec_scraper import EnhancedNovDecScraper
from scripts.human_review_alert import HumanReviewAlert
from scripts.verify_automation_pipeline import AutomationVerifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "logs" / f"section_1_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
FINAL_REPORT_JSON = DATA_DIR / "section_1_complete_report.json"


def execute_section_1_1(dry_run: bool = False) -> dict:
    """
    Execute Section 1.1: Automated Incident Scraper Execution & Validation
    
    Returns:
        Scraper results dictionary
    """
    logger.info("=" * 70)
    logger.info("SECTION 1.1: AUTOMATED INCIDENT SCRAPER EXECUTION")
    logger.info("=" * 70)
    
    try:
        scraper = EnhancedNovDecScraper(dry_run=dry_run)
        results = scraper.run()
        
        # Generate human review alert if there are pending incidents
        if results["summary"]["pending_human_review_medium_confidence"] > 0:
            logger.info("\nGenerating human review alert...")
            alert = HumanReviewAlert()
            email_content = alert.generate_alert()
            
            if email_content:
                # Save alert to file
                alert.save_alert_to_file(
                    email_content,
                    DATA_DIR / f"review_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                logger.info("Human review alert generated and saved")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in Section 1.1: {e}", exc_info=True)
        raise


def execute_section_1_2() -> dict:
    """
    Execute Section 1.2: Automated Scanning System Operational Verification
    
    Returns:
        Verification report dictionary
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 1.2: AUTOMATED SCANNING SYSTEM VERIFICATION")
    logger.info("=" * 70)
    
    try:
        verifier = AutomationVerifier(
            github_token=os.getenv("GITHUB_TOKEN"),
            repo=os.getenv("GITHUB_REPOSITORY")
        )
        
        report = verifier.verify_all()
        verifier.save_report()
        
        return report
        
    except Exception as e:
        logger.error(f"Error in Section 1.2: {e}", exc_info=True)
        raise


def generate_comprehensive_report(section_1_1_results: dict, section_1_2_results: dict) -> dict:
    """
    Generate comprehensive status report combining both sections.
    
    Returns:
        Complete report dictionary
    """
    report = {
        "execution_info": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "section_1_1": "Completed",
            "section_1_2": "Completed",
        },
        "section_1_1_results": section_1_1_results,
        "section_1_2_results": section_1_2_results,
        "summary": {
            "overall_status": section_1_2_results.get("overall_status", "Unknown"),
            "incidents_scraped": section_1_1_results.get("summary", {}).get("total_incidents_scraped", 0),
            "added_to_map": section_1_1_results.get("summary", {}).get("added_to_map_high_confidence", 0),
            "pending_review": section_1_1_results.get("summary", {}).get("pending_human_review_medium_confidence", 0),
            "automation_status": section_1_2_results.get("overall_status", "Unknown"),
        },
        "recommendations": section_1_2_results.get("recommendations", []),
    }
    
    return report


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Execute Section 1: Incident Data Audit & Expansion"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without saving files (for testing)"
    )
    parser.add_argument(
        "--skip-1-1",
        action="store_true",
        help="Skip Section 1.1 (scraper execution)"
    )
    parser.add_argument(
        "--skip-1-2",
        action="store_true",
        help="Skip Section 1.2 (verification)"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("=" * 70)
        logger.info("SECTION 1: INCIDENT DATA AUDIT & EXPANSION")
        logger.info("=" * 70)
        logger.info(f"Execution started: {datetime.now(timezone.utc).isoformat()}")
        logger.info("=" * 70)
        
        section_1_1_results = None
        section_1_2_results = None
        
        # Execute Section 1.1
        if not args.skip_1_1:
            section_1_1_results = execute_section_1_1(dry_run=args.dry_run)
        else:
            logger.info("Skipping Section 1.1 (scraper execution)")
        
        # Execute Section 1.2
        if not args.skip_1_2:
            section_1_2_results = execute_section_1_2()
        else:
            logger.info("Skipping Section 1.2 (verification)")
        
        # Generate comprehensive report
        if section_1_1_results and section_1_2_results:
            comprehensive_report = generate_comprehensive_report(
                section_1_1_results,
                section_1_2_results
            )
            
            # Save report
            if not args.dry_run:
                with open(FINAL_REPORT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(comprehensive_report, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"\nComprehensive report saved to {FINAL_REPORT_JSON}")
            
            # Print summary
            print("\n" + "=" * 70)
            print("SECTION 1 EXECUTION COMPLETE")
            print("=" * 70)
            status = comprehensive_report['summary']['overall_status']
            status_clean = status.replace("✅", "[OK]").replace("⚠️", "[WARN]").replace("❌", "[FAIL]")
            print(f"Overall Automation Status: {status_clean}")
            print(f"Incidents Scraped: {comprehensive_report['summary']['incidents_scraped']}")
            print(f"Added to Map (HIGH confidence): {comprehensive_report['summary']['added_to_map']}")
            print(f"Pending Review (MEDIUM confidence): {comprehensive_report['summary']['pending_review']}")
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

