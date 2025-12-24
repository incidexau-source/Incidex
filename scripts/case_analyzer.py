#!/usr/bin/env python3
"""
Case Analyzer
=============
Analyzes legal case judgments using GPT-4 to extract:
- Legal reasoning and precedent
- Key findings and holdings
- Impact assessment on LGBTQ+ rights
- Legal principles established
- Dissenting opinions
- Landmark/precedent-setting decisions
"""

import os
import sys
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

import pandas as pd
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI
    from config import OPENAI_API_KEY, RATE_LIMIT_DELAY
    HAS_OPENAI = True
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except:
    HAS_OPENAI = False
    client = None

# Setup
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CASES_FILE = DATA_DIR / "legal-cases.csv"
ANALYSIS_FILE = DATA_DIR / "case-analysis.csv"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def download_judgment_text(judgment_url: str) -> str:
    """Download and extract text from judgment URL (PDF or HTML)."""
    if not judgment_url:
        return ""
    
    try:
        response = requests.get(judgment_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; CaseAnalyzer/1.0)'
        })
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'pdf' in content_type or judgment_url.lower().endswith('.pdf'):
                # Try to extract text from PDF
                try:
                    import PyPDF2
                    from io import BytesIO
                    
                    pdf_file = BytesIO(response.content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    text = ""
                    for page in pdf_reader.pages[:10]:  # First 10 pages
                        text += page.extract_text() + "\n"
                    
                    return text[:50000]  # Limit to 50k chars
                except Exception as e:
                    logger.warning(f"PDF extraction failed: {e}")
                    return ""
            else:
                # HTML text extraction
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text(separator='\n', strip=True)
                return text[:50000]  # Limit to 50k chars
        
    except Exception as e:
        logger.warning(f"Error downloading judgment: {e}")
    
    return ""


def calculate_importance_score(case_data: Dict, analysis_data: Dict) -> int:
    """
    Calculate importance score (1-10) based on:
    - Court level
    - Precedent impact
    - Scope of impact
    - Media attention (if available)
    - Number of interested parties
    """
    score = 1
    
    # Court level (1-4 points)
    court = case_data.get('court', '').lower()
    if 'high court' in court:
        score += 4
    elif 'federal court' in court:
        score += 3
    elif 'supreme court' in court:
        score += 2
    else:
        score += 1
    
    # Precedent level (1-3 points)
    precedent_level = analysis_data.get('precedent_level', '').lower()
    if precedent_level == 'binding':
        score += 3
    elif precedent_level == 'persuasive':
        score += 2
    elif precedent_level == 'limited':
        score += 1
    
    # Impact level (1-2 points)
    impact_level = case_data.get('impact_level', '').lower()
    if impact_level == 'high':
        score += 2
    elif impact_level == 'medium':
        score += 1
    
    # Scope of impact (1-2 points)
    affected = analysis_data.get('affected_populations', '')
    if 'nationwide' in affected.lower() or 'national' in affected.lower():
        score += 2
    elif affected:
        score += 1
    
    # Ensure score is between 1-10
    return min(10, max(1, score))


def analyze_case_with_gpt(case_data: Dict, judgment_text: str = "") -> Dict:
    """
    Analyze case using GPT-4 to extract legal principles and impact.
    """
    case_name = case_data.get('case_name', '')
    court = case_data.get('court', '')
    citation = case_data.get('citation', '')
    case_summary = case_data.get('case_summary', '')
    
    # Build analysis text
    analysis_text = f"Case: {case_name}\n"
    analysis_text += f"Court: {court}\n"
    analysis_text += f"Citation: {citation}\n"
    analysis_text += f"Summary: {case_summary}\n"
    
    if judgment_text:
        analysis_text += f"\nJudgment Text (excerpt):\n{judgment_text[:10000]}\n"
    
    prompt = f"""Analyze this Australian legal case for LGBTQ+ rights impact.

{analysis_text}

Extract and analyze:
1. Legal principles established or applied
2. Key findings and holdings
3. Impact assessment on LGBTQ+ rights (positive/negative/neutral)
4. Precedent level (binding/persuasive/limited)
5. Affected populations (individuals, organizations, policy, nationwide)
6. Future implications for LGBTQ+ rights
7. Any dissenting opinions and their arguments
8. Whether this is a landmark or precedent-setting decision

Return ONLY valid JSON (no markdown):
{{
    "legal_principles": "List of key legal principles established or applied",
    "key_findings": "Summary of key findings and holdings",
    "impact_assessment": "Detailed assessment of impact on LGBTQ+ rights",
    "precedent_level": "binding|persuasive|limited",
    "affected_populations": "Description of who is affected (individuals, organizations, policy, nationwide)",
    "future_implications": "Analysis of future implications for LGBTQ+ rights",
    "dissenting_opinions": "Summary of dissenting opinions if any, else 'None'",
    "is_landmark": true/false,
    "landmark_reason": "Reason if landmark case, else empty string"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean JSON
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        analysis = json.loads(result_text)
        
        # Calculate importance score
        importance_score = calculate_importance_score(case_data, analysis)
        analysis['importance_score'] = importance_score
        
        return analysis
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Response: {result_text[:500]}")
        return {}
    except Exception as e:
        logger.error(f"GPT analysis error: {e}")
        return {}


def load_existing_analyses() -> Dict[str, Dict]:
    """Load existing case analyses."""
    existing = {}
    
    if ANALYSIS_FILE.exists():
        try:
            df = pd.read_csv(ANALYSIS_FILE)
            for _, row in df.iterrows():
                case_id = row.get('case_id', '')
                if case_id:
                    existing[case_id] = row.to_dict()
        except Exception as e:
            logger.warning(f"Error loading existing analyses: {e}")
    
    return existing


def save_analyses(analyses: List[Dict]):
    """Save case analyses to CSV."""
    if not analyses:
        return
    
    # Load existing analyses
    existing = load_existing_analyses()
    
    # Merge new analyses
    for analysis in analyses:
        case_id = analysis.get('case_id', '')
        if case_id:
            existing[case_id] = analysis
    
    # Convert to DataFrame and save
    df = pd.DataFrame(list(existing.values()))
    
    # Ensure all required columns exist
    required_columns = [
        'case_id', 'legal_principles', 'key_findings', 'impact_assessment',
        'importance_score', 'precedent_level', 'affected_populations',
        'future_implications'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(ANALYSIS_FILE, index=False)
    logger.info(f"Saved {len(df)} case analyses to {ANALYSIS_FILE}")


def analyze_cases(force_reanalyze: bool = False) -> List[Dict]:
    """Analyze all cases that need analysis."""
    if not CASES_FILE.exists():
        logger.warning(f"Cases file not found: {CASES_FILE}")
        return []
    
    if not HAS_OPENAI or not client:
        logger.error("OpenAI API not available")
        return []
    
    # Load cases
    try:
        df = pd.read_csv(CASES_FILE)
    except Exception as e:
        logger.error(f"Error loading cases: {e}")
        return []
    
    # Load existing analyses
    existing = load_existing_analyses()
    
    # Filter cases that need analysis
    cases_to_analyze = []
    for _, row in df.iterrows():
        case_id = row.get('case_id', '')
        
        if not case_id:
            continue
        
        # Skip if already analyzed (unless force_reanalyze)
        if not force_reanalyze and case_id in existing:
            continue
        
        # Only analyze LGBTQ+ relevant cases
        relevance = row.get('lgbtq_relevance', '')
        if relevance and relevance != 'none':
            cases_to_analyze.append(row.to_dict())
    
    logger.info(f"Found {len(cases_to_analyze)} cases to analyze")
    
    # Analyze cases
    analyses = []
    
    for idx, case_data in enumerate(cases_to_analyze, 1):
        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', '')
        
        logger.info(f"[{idx}/{len(cases_to_analyze)}] Analyzing: {case_name[:50]}...")
        
        # Download judgment text if available
        judgment_url = case_data.get('full_judgment_url', '') or case_data.get('url', '')
        judgment_text = ""
        
        if judgment_url:
            logger.info(f"  Downloading judgment from {judgment_url[:80]}...")
            judgment_text = download_judgment_text(judgment_url)
            if judgment_text:
                logger.info(f"  Downloaded {len(judgment_text)} characters")
        
        # Analyze with GPT
        analysis = analyze_case_with_gpt(case_data, judgment_text)
        
        if analysis:
            analysis['case_id'] = case_id
            analyses.append(analysis)
            logger.info(f"  ✓ Analyzed (importance: {analysis.get('importance_score', 'N/A')}/10)")
        else:
            logger.warning(f"  ✗ Analysis failed")
        
        # Rate limiting
        import time
        time.sleep(RATE_LIMIT_DELAY)
    
    return analyses


def main():
    """Main function."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Case Analyzer")
    logger.info("=" * 60)
    
    analyses = analyze_cases(force_reanalyze=False)
    
    if analyses:
        save_analyses(analyses)
        logger.info(f"\n✓ Analyzed {len(analyses)} cases")
    else:
        logger.info("\n✓ No cases to analyze")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

