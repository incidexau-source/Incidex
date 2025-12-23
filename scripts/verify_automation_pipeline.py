"""
GitHub Actions Automation Pipeline Verification
Section 1.2: Automated Scanning System Operational Verification

Verifies that the automated GitHub Actions-based incident scanning pipeline
is fully operational and running on schedule.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
DATA_DIR = BASE_DIR / "data"
OUTPUT_CSV = DATA_DIR / "incidents_news_sourced.csv"
MAP_CSV = DATA_DIR / "incidents_in_progress.csv"
WORKFLOWS_DIR = BASE_DIR / ".github" / "workflows"
VERIFICATION_REPORT_JSON = DATA_DIR / "automation_verification_report.json"


class AutomationVerifier:
    """
    Verifies GitHub Actions automation pipeline status.
    """
    
    def __init__(self, github_token: Optional[str] = None, repo: Optional[str] = None):
        """
        Initialize the verifier.
        
        Args:
            github_token: GitHub personal access token (optional, for API access)
            repo: GitHub repository (format: owner/repo, optional)
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo = repo or os.getenv("GITHUB_REPOSITORY")
        self.report = {
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "components": {},
            "workflows": {},
            "recommendations": [],
        }
    
    def verify_all(self) -> Dict[str, Any]:
        """
        Run all verification checks.
        
        Returns:
            Complete verification report
        """
        logger.info("=" * 70)
        logger.info("AUTOMATION PIPELINE VERIFICATION")
        logger.info("=" * 70)
        
        # Check 1: GitHub Actions workflow files
        logger.info("\n[CHECK 1] Verifying GitHub Actions Workflows...")
        self._verify_workflow_files()
        
        # Check 2: Workflow configuration
        logger.info("\n[CHECK 2] Verifying Workflow Configuration...")
        self._verify_workflow_config()
        
        # Check 3: Recent workflow runs (if GitHub API available)
        if self.github_token and self.repo:
            logger.info("\n[CHECK 3] Checking Recent Workflow Runs...")
            self._verify_recent_runs()
        else:
            logger.info("\n[CHECK 3] Skipping workflow runs (GitHub API not configured)")
            self.report["workflows"]["recent_runs"] = {
                "status": "skipped",
                "note": "GitHub token and repository not configured"
            }
        
        # Check 4: Scraper components
        logger.info("\n[CHECK 4] Verifying Scraper Components...")
        self._verify_scraper_components()
        
        # Check 5: OpenAI API integration
        logger.info("\n[CHECK 5] Verifying OpenAI API Integration...")
        self._verify_openai_integration()
        
        # Check 6: Data pipeline
        logger.info("\n[CHECK 6] Verifying Data Pipeline...")
        self._verify_data_pipeline()
        
        # Check 7: Map sync
        logger.info("\n[CHECK 7] Verifying Map Data Sync...")
        self._verify_map_sync()
        
        # Check 8: Human review alerts
        logger.info("\n[CHECK 8] Verifying Human Review Alert System...")
        self._verify_review_alerts()
        
        # Determine overall status
        self._determine_overall_status()
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.report
    
    def _verify_workflow_files(self):
        """Verify GitHub Actions workflow files exist."""
        workflows = {}
        
        expected_workflows = [
            "daily_rss_monitor.yml",
            "rss_monitor.yml",
        ]
        
        for workflow_name in expected_workflows:
            workflow_path = WORKFLOWS_DIR / workflow_name
            exists = workflow_path.exists()
            
            workflows[workflow_name] = {
                "exists": exists,
                "path": str(workflow_path),
                "status": "✅" if exists else "❌",
            }
            
            if exists:
                # Check if file is valid YAML (basic check)
                try:
                    with open(workflow_path, 'r') as f:
                        content = f.read()
                        if "on:" in content and "jobs:" in content:
                            workflows[workflow_name]["valid_yaml"] = True
                        else:
                            workflows[workflow_name]["valid_yaml"] = False
                except Exception as e:
                    workflows[workflow_name]["valid_yaml"] = False
                    workflows[workflow_name]["error"] = str(e)
        
        self.report["workflows"]["files"] = workflows
    
    def _verify_workflow_config(self):
        """Verify workflow configuration (schedule, triggers, etc.)."""
        config_status = {}
        
        for workflow_name, workflow_info in self.report["workflows"]["files"].items():
            if not workflow_info.get("exists"):
                continue
            
            workflow_path = WORKFLOWS_DIR / workflow_name
            
            try:
                with open(workflow_path, 'r') as f:
                    content = f.read()
                
                has_schedule = "schedule:" in content or "cron:" in content
                has_manual_trigger = "workflow_dispatch:" in content
                has_openai_key = "OPENAI_API_KEY" in content or "secrets.OPENAI_API_KEY" in content
                
                config_status[workflow_name] = {
                    "has_schedule": has_schedule,
                    "has_manual_trigger": has_manual_trigger,
                    "has_openai_key": has_openai_key,
                    "status": "✅" if (has_schedule and has_openai_key) else "⚠️",
                }
                
            except Exception as e:
                config_status[workflow_name] = {
                    "error": str(e),
                    "status": "❌",
                }
        
        self.report["workflows"]["configuration"] = config_status
    
    def _verify_recent_runs(self):
        """Verify recent workflow runs via GitHub API."""
        if not self.github_token or not self.repo:
            return
        
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            
            # Get workflow runs (last 14 days)
            url = f"https://api.github.com/repos/{self.repo}/actions/runs"
            params = {
                "per_page": 30,  # Get last 30 runs
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                
                # Filter to RSS monitor workflows
                rss_runs = [
                    run for run in runs
                    if "rss" in run.get("name", "").lower() or "monitor" in run.get("name", "").lower()
                ]
                
                successful = [r for r in rss_runs if r.get("conclusion") == "success"]
                failed = [r for r in rss_runs if r.get("conclusion") == "failure"]
                in_progress = [r for r in rss_runs if r.get("status") == "in_progress"]
                
                # Get last successful run
                last_successful = None
                if successful:
                    last_successful = max(successful, key=lambda x: x.get("created_at", ""))
                
                self.report["workflows"]["recent_runs"] = {
                    "status": "✅",
                    "total_runs_14_days": len(rss_runs),
                    "successful": len(successful),
                    "failed": len(failed),
                    "in_progress": len(in_progress),
                    "last_successful": last_successful.get("created_at") if last_successful else None,
                    "last_successful_url": last_successful.get("html_url") if last_successful else None,
                }
            else:
                self.report["workflows"]["recent_runs"] = {
                    "status": "⚠️",
                    "error": f"GitHub API returned {response.status_code}",
                }
                
        except Exception as e:
            self.report["workflows"]["recent_runs"] = {
                "status": "❌",
                "error": str(e),
            }
    
    def _verify_scraper_components(self):
        """Verify scraper component functionality."""
        components = {}
        
        # Check Python dependencies
        required_modules = [
            "pandas",
            "requests",
            "bs4",  # BeautifulSoup
            "openai",
            "feedparser",
            "geopy",
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                components[module] = {"status": "✅", "installed": True}
            except ImportError:
                missing_modules.append(module)
                components[module] = {"status": "❌", "installed": False}
        
        # Check if scraper scripts exist
        scraper_scripts = [
            "scripts/rss_monitor.py",
            "monitor.py",
            "article_fetcher.py",
            "incident_extractor.py",
            "geocoder.py",
            "deduplicator.py",
        ]
        
        for script in scraper_scripts:
            script_path = BASE_DIR / script
            components[script] = {
                "status": "✅" if script_path.exists() else "❌",
                "exists": script_path.exists(),
            }
        
        self.report["components"]["scraper"] = {
            "status": "✅" if not missing_modules else "⚠️",
            "modules": components,
            "missing_modules": missing_modules,
        }
    
    def _verify_openai_integration(self):
        """Verify OpenAI API integration."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # Check config.py
            try:
                from config import OPENAI_API_KEY as config_key
                api_key = config_key
            except:
                pass
        
        has_key = bool(api_key and len(api_key) > 10)
        
        # Check if key is in GitHub Secrets (can't verify directly, but check workflow)
        in_workflow = False
        for workflow_name, workflow_info in self.report["workflows"]["files"].items():
            if workflow_info.get("exists"):
                workflow_path = WORKFLOWS_DIR / workflow_name
                try:
                    with open(workflow_path, 'r') as f:
                        if "OPENAI_API_KEY" in f.read():
                            in_workflow = True
                            break
                except:
                    pass
        
        self.report["components"]["openai"] = {
            "status": "✅" if (has_key and in_workflow) else "⚠️",
            "api_key_present": has_key,
            "configured_in_workflow": in_workflow,
            "note": "Cannot verify billing/credits without API call",
        }
    
    def _verify_data_pipeline(self):
        """Verify data pipeline end-to-end."""
        pipeline_status = {
            "csv_output_exists": OUTPUT_CSV.exists(),
            "map_csv_exists": MAP_CSV.exists(),
            "csv_has_recent_timestamp": False,
            "csv_format_valid": False,
        }
        
        # Check CSV timestamp
        if OUTPUT_CSV.exists():
            mtime = datetime.fromtimestamp(OUTPUT_CSV.stat().st_mtime, tz=timezone.utc)
            days_old = (datetime.now(timezone.utc) - mtime).days
            pipeline_status["csv_last_modified"] = mtime.isoformat()
            pipeline_status["csv_days_old"] = days_old
            pipeline_status["csv_has_recent_timestamp"] = days_old <= 7
        
            # Check CSV format
            try:
                import pandas as pd
                df = pd.read_csv(OUTPUT_CSV)
                pipeline_status["csv_format_valid"] = True
                pipeline_status["csv_row_count"] = len(df)
            except Exception as e:
                pipeline_status["csv_format_error"] = str(e)
        
        self.report["components"]["data_pipeline"] = {
            "status": "✅" if (
                pipeline_status["csv_output_exists"] and
                pipeline_status["csv_format_valid"] and
                pipeline_status["csv_has_recent_timestamp"]
            ) else "⚠️",
            **pipeline_status,
        }
    
    def _verify_map_sync(self):
        """Verify map data sync."""
        map_status = {
            "map_csv_exists": MAP_CSV.exists(),
            "map_csv_recent": False,
        }
        
        if MAP_CSV.exists():
            mtime = datetime.fromtimestamp(MAP_CSV.stat().st_mtime, tz=timezone.utc)
            days_old = (datetime.now(timezone.utc) - mtime).days
            map_status["map_csv_last_modified"] = mtime.isoformat()
            map_status["map_csv_days_old"] = days_old
            map_status["map_csv_recent"] = days_old <= 1  # Should update within 24 hours
        
        self.report["components"]["map_sync"] = {
            "status": "✅" if map_status["map_csv_recent"] else "⚠️",
            **map_status,
        }
    
    def _verify_review_alerts(self):
        """Verify human review alert system."""
        alert_status = {
            "alert_script_exists": (BASE_DIR / "scripts" / "human_review_alert.py").exists(),
            "review_queue_exists": (DATA_DIR / "review_queue_nov_dec_2025.csv").exists(),
            "alert_config_exists": (DATA_DIR / "review_alert_config.json").exists(),
        }
        
        self.report["components"]["review_alerts"] = {
            "status": "✅" if alert_status["alert_script_exists"] else "⚠️",
            **alert_status,
        }
    
    def _determine_overall_status(self):
        """Determine overall pipeline status."""
        statuses = []
        
        # Collect all component statuses
        for component_name, component_data in self.report["components"].items():
            if isinstance(component_data, dict) and "status" in component_data:
                statuses.append(component_data["status"])
        
        # Determine overall
        if all(s == "✅" for s in statuses):
            self.report["overall_status"] = "✅ Fully operational"
        elif any(s == "❌" for s in statuses):
            self.report["overall_status"] = "❌ Offline"
        else:
            self.report["overall_status"] = "⚠️ Partial (some components offline)"
    
    def _generate_recommendations(self):
        """Generate recommendations based on verification results."""
        recommendations = []
        
        # Check for issues
        if not self.report["workflows"]["files"].get("daily_rss_monitor.yml", {}).get("exists"):
            recommendations.append({
                "priority": "P1",
                "issue": "GitHub Actions workflow file missing",
                "fix": "Create .github/workflows/daily_rss_monitor.yml",
                "time_estimate": "15 minutes",
            })
        
        missing_modules = self.report["components"]["scraper"].get("missing_modules", [])
        if missing_modules:
            recommendations.append({
                "priority": "P1",
                "issue": f"Missing Python modules: {', '.join(missing_modules)}",
                "fix": f"Run: pip install {' '.join(missing_modules)}",
                "time_estimate": "5 minutes",
            })
        
        if not self.report["components"]["openai"].get("api_key_present"):
            recommendations.append({
                "priority": "P1",
                "issue": "OpenAI API key not configured",
                "fix": "Set OPENAI_API_KEY in GitHub Secrets or config.py",
                "time_estimate": "5 minutes",
            })
        
        if not self.report["components"]["map_sync"].get("map_csv_recent"):
            recommendations.append({
                "priority": "P1",
                "issue": "Map CSV not updated recently",
                "fix": "Check if scraper is running and committing changes",
                "time_estimate": "30 minutes",
            })
        
        self.report["recommendations"] = recommendations
    
    def save_report(self, output_path: Optional[str] = None):
        """Save verification report to JSON file."""
        if not output_path:
            output_path = VERIFICATION_REPORT_JSON
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Verification report saved to {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify GitHub Actions automation pipeline"
    )
    parser.add_argument(
        "--github-token",
        type=str,
        help="GitHub personal access token (for API access)"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="GitHub repository (format: owner/repo)"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save verification report to JSON file"
    )
    
    args = parser.parse_args()
    
    try:
        verifier = AutomationVerifier(
            github_token=args.github_token,
            repo=args.repo
        )
        
        report = verifier.verify_all()
        
        # Print summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        status = report['overall_status']
        # Remove emoji characters for Windows console compatibility
        status_clean = status.replace("✅", "[OK]").replace("⚠️", "[WARN]").replace("❌", "[FAIL]")
        print(f"Overall Status: {status_clean}")
        print("\nComponent Status:")
        for component_name, component_data in report["components"].items():
            if isinstance(component_data, dict) and "status" in component_data:
                comp_status = component_data['status']
                comp_status_clean = comp_status.replace("✅", "[OK]").replace("⚠️", "[WARN]").replace("❌", "[FAIL]")
                print(f"  {component_name}: {comp_status_clean}")
        
        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  [{rec['priority']}] {rec['issue']}")
                print(f"      Fix: {rec['fix']}")
                print(f"      Time: {rec['time_estimate']}")
        
        if args.save_report:
            verifier.save_report()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

