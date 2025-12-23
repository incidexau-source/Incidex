#!/usr/bin/env python3
"""
Automation Status Verification Script
Section 1.2: Verify GitHub Actions workflow and automation systems

Checks:
- GitHub Actions workflow files exist and are valid
- Python scripts are functional
- Dependencies are available
- Configuration is correct
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parents[1]
GITHUB_WORKFLOWS_DIR = BASE_DIR / ".github" / "workflows"

def check_file_exists(path: Path, description: str) -> tuple[bool, str]:
    """Check if a file exists."""
    exists = path.exists()
    message = f"{description}: {'[OK] EXISTS' if exists else '[MISSING] NOT FOUND'}"
    if exists:
        message += f" ({path.stat().st_size} bytes)"
    return exists, message

def check_python_import(module: str) -> tuple[bool, str]:
    """Check if a Python module can be imported."""
    try:
        __import__(module)
        return True, f"[OK] {module} available"
    except ImportError as e:
        return False, f"[MISS] {module} not available: {e}"

def check_github_workflow(workflow_file: Path) -> Dict[str, Any]:
    """Check a GitHub Actions workflow file."""
    result = {
        "file": str(workflow_file),
        "exists": False,
        "valid_yaml": False,
        "has_schedule": False,
        "has_manual_trigger": False,
        "has_openai_key": False,
        "errors": []
    }
    
    if not workflow_file.exists():
        result["errors"].append("Workflow file not found")
        return result
    
    result["exists"] = True
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic checks (not full YAML parsing, just pattern matching)
        if "schedule:" in content or "cron:" in content:
            result["has_schedule"] = True
        
        if "workflow_dispatch:" in content:
            result["has_manual_trigger"] = True
        
        if "OPENAI_API_KEY" in content or "secrets.OPENAI_API_KEY" in content:
            result["has_openai_key"] = True
            
        # Try to validate as YAML (basic)
        try:
            import yaml
            with open(workflow_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            result["valid_yaml"] = True
        except ImportError:
            result["errors"].append("PyYAML not installed, cannot validate YAML syntax")
        except Exception as e:
            result["errors"].append(f"YAML validation error: {e}")
            
    except Exception as e:
        result["errors"].append(f"Error reading workflow: {e}")
    
    return result

def check_script_imports(script_path: Path) -> Dict[str, Any]:
    """Check if a Python script can be imported and has required dependencies."""
    result = {
        "script": str(script_path),
        "exists": False,
        "syntax_valid": False,
        "imports_ok": False,
        "missing_modules": [],
        "errors": []
    }
    
    if not script_path.exists():
        result["errors"].append("Script file not found")
        return result
    
    result["exists"] = True
    
    # Check syntax
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(script_path), 'exec')
        result["syntax_valid"] = True
    except SyntaxError as e:
        result["errors"].append(f"Syntax error: {e}")
        return result
    except Exception as e:
        result["errors"].append(f"Error checking syntax: {e}")
        return result
    
    # Check imports (read file and check for common imports)
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common dependencies
        imports_to_check = [
            'pandas', 'requests', 'beautifulsoup4', 'selenium', 
            'openai', 'feedparser', 'geopy'
        ]
        
        for module in imports_to_check:
            # Check if module is imported
            if f"import {module}" in content or f"from {module}" in content:
                try:
                    __import__(module.replace('-', '_').replace('4', ''))
                except ImportError:
                    result["missing_modules"].append(module)
        
        result["imports_ok"] = len(result["missing_modules"]) == 0
        
    except Exception as e:
        result["errors"].append(f"Error checking imports: {e}")
    
    return result

def check_environment_variables() -> Dict[str, Any]:
    """Check for required environment variables."""
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["GITHUB_TOKEN", "GEOCODING_API_KEY"]
    
    result = {
        "required": {},
        "optional": {},
        "all_required_present": True
    }
    
    for var in required_vars:
        value = os.getenv(var)
        present = value is not None and value.strip() != ""
        result["required"][var] = {
            "present": present,
            "length": len(value) if value else 0,
            "preview": f"{value[:10]}..." if value and len(value) > 10 else "N/A"
        }
        if not present:
            result["all_required_present"] = False
    
    for var in optional_vars:
        value = os.getenv(var)
        result["optional"][var] = {
            "present": value is not None and value.strip() != "",
            "length": len(value) if value else 0
        }
    
    return result

def check_data_files() -> Dict[str, Any]:
    """Check if required data files exist."""
    data_dir = BASE_DIR / "data"
    required_files = [
        "incidents_in_progress.csv",
        "incidents_extracted.csv",
        "incidents_2015_2025_complete.csv"
    ]
    
    result = {
        "data_dir_exists": data_dir.exists(),
        "files": {}
    }
    
    for filename in required_files:
        filepath = data_dir / filename
        exists = filepath.exists()
        result["files"][filename] = {
            "exists": exists,
            "size": filepath.stat().st_size if exists else 0,
            "path": str(filepath)
        }
    
    return result

def main():
    """Run all verification checks."""
    print("=" * 70)
    print("AUTOMATION STATUS VERIFICATION")
    print("Section 1.2: GitHub Actions & Automation Systems")
    print("=" * 70)
    print(f"\nBase Directory: {BASE_DIR}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    results = {
        "workflows": {},
        "scripts": {},
        "environment": {},
        "data_files": {},
        "python_modules": {}
    }
    
    # 1. Check GitHub Actions workflows
    print("1. GITHUB ACTIONS WORKFLOWS")
    print("-" * 70)
    
    if GITHUB_WORKFLOWS_DIR.exists():
        workflow_files = list(GITHUB_WORKFLOWS_DIR.glob("*.yml")) + list(GITHUB_WORKFLOWS_DIR.glob("*.yaml"))
        
        for workflow_file in workflow_files:
            print(f"\nChecking: {workflow_file.name}")
            result = check_github_workflow(workflow_file)
            results["workflows"][workflow_file.name] = result
            
        print(f"  Exists: {result['exists']}")
        print(f"  Valid YAML: {result['valid_yaml']}")
        print(f"  Has Schedule: {result['has_schedule']}")
        print(f"  Has Manual Trigger: {result['has_manual_trigger']}")
        print(f"  References OpenAI Key: {result['has_openai_key']}")
        if result['errors']:
            print(f"  Errors: {', '.join(result['errors'])}")
    else:
        print(f"[ERROR] Workflows directory not found: {GITHUB_WORKFLOWS_DIR}")
    
    # 2. Check Python scripts
    print("\n\n2. PYTHON SCRIPTS")
    print("-" * 70)
    
    scripts_to_check = [
        BASE_DIR / "scripts" / "rss_monitor.py",
        BASE_DIR / "scripts" / "daily_scraper.py",
        BASE_DIR / "monitor.py",
        BASE_DIR / "article_fetcher.py",
        BASE_DIR / "incident_extractor.py",
        BASE_DIR / "geocoder.py",
    ]
    
    for script_path in scripts_to_check:
        if script_path.exists():
            print(f"\nChecking: {script_path.name}")
            result = check_script_imports(script_path)
            results["scripts"][script_path.name] = result
            
            print(f"  Exists: {result['exists']}")
            print(f"  Syntax Valid: {result['syntax_valid']}")
            print(f"  Imports OK: {result['imports_ok']}")
            if result['missing_modules']:
                print(f"  Missing Modules: {', '.join(result['missing_modules'])}")
            if result['errors']:
                print(f"  Errors: {', '.join(result['errors'])}")
        else:
            print(f"\n[ERROR] Script not found: {script_path.name}")
    
    # 3. Check Python modules/dependencies
    print("\n\n3. PYTHON MODULES & DEPENDENCIES")
    print("-" * 70)
    
    modules_to_check = [
        "pandas", "requests", "bs4", "selenium", "openai", 
        "feedparser", "geopy", "yaml"
    ]
    
    for module in modules_to_check:
        available, message = check_python_import(module)
        results["python_modules"][module] = available
        print(f"  {message}")
    
    # 4. Check environment variables
    print("\n\n4. ENVIRONMENT VARIABLES")
    print("-" * 70)
    
    env_result = check_environment_variables()
    results["environment"] = env_result
    
    print("\nRequired Variables:")
    for var, info in env_result["required"].items():
        status = "[OK]" if info["present"] else "[MISS]"
        print(f"  {status} {var}: {'SET' if info['present'] else 'NOT SET'}")
        if info["present"]:
            print(f"      Length: {info['length']} characters")
    
    print("\nOptional Variables:")
    for var, info in env_result["optional"].items():
        status = "[OK]" if info["present"] else "[ - ]"
        print(f"  {status} {var}: {'SET' if info['present'] else 'NOT SET'}")
    
    # 5. Check data files
    print("\n\n5. DATA FILES")
    print("-" * 70)
    
    data_result = check_data_files()
    results["data_files"] = data_result
    
    print(f"Data Directory Exists: {data_result['data_dir_exists']}")
    for filename, info in data_result["files"].items():
        status = "[OK]" if info["exists"] else "[MISS]"
        size_mb = info["size"] / (1024 * 1024) if info["exists"] else 0
        print(f"  {status} {filename}: {'EXISTS' if info['exists'] else 'MISSING'}")
        if info["exists"]:
            print(f"      Size: {size_mb:.2f} MB")
    
    # Generate summary
    print("\n\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    # Count issues
    issues = []
    
    # Workflows
    if not results["workflows"]:
        issues.append("No workflow files found")
    else:
        for name, result in results["workflows"].items():
            if not result["exists"]:
                issues.append(f"Workflow {name} not found")
            if not result["valid_yaml"] and result["exists"]:
                issues.append(f"Workflow {name} has YAML issues")
            if not result["has_schedule"] and result["exists"]:
                issues.append(f"Workflow {name} missing schedule")
            if not result["has_openai_key"] and result["exists"]:
                issues.append(f"Workflow {name} missing OpenAI key reference")
    
    # Environment
    if not env_result["all_required_present"]:
        issues.append("Required environment variables not set")
    
    # Python modules
    missing_modules = [m for m, available in results["python_modules"].items() if not available]
    if missing_modules:
        issues.append(f"Missing Python modules: {', '.join(missing_modules)}")
    
    if issues:
        print(f"\n[!] {len(issues)} ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[OK] ALL CHECKS PASSED")
    
    # Save detailed report
    report_file = BASE_DIR / "data" / "automation_status_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[OK] Detailed report saved to: {report_file}")
    
    # Generate status assessment
    print("\n" + "=" * 70)
    print("STATUS ASSESSMENT")
    print("=" * 70)
    
    if len(issues) == 0:
        print("\n[OK] FULLY OPERATIONAL")
        print("   All systems appear to be configured correctly.")
        print("   Note: Runtime verification (actual workflow execution)")
        print("   requires access to GitHub Actions dashboard/logs.")
    elif len(issues) <= 3:
        print("\n[!] PARTIAL - Minor Issues")
        print("   Most systems operational, but some issues need attention.")
    else:
        print("\n[ERROR] OFFLINE - Major Issues")
        print("   Multiple issues detected. System may not function correctly.")
    
    return 0 if len(issues) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

