#!/usr/bin/env python3
"""
Precedent Tracker
================
Tracks how past LGBTQ+ cases are cited in new cases:
- Which cases cite which previous cases
- Citation context (followed, distinguished, overruled)
- Evolution of legal interpretation
- Changes in judicial approach to LGBTQ+ issues
- Landmark cases that establish new legal principles
- Cases that overrule or modify previous precedent
"""

import os
import sys
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

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
PRECEDENTS_FILE = DATA_DIR / "case-precedents.csv"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def extract_case_citations(text: str) -> List[Tuple[str, str]]:
    """
    Extract case citations from text.
    Returns list of (citation, context) tuples.
    """
    citations = []
    
    # Common citation patterns
    patterns = [
        # [Year] Court Abbreviation Number
        r'\[(\d{4})\]\s*([A-Z]{2,10})\s*(\d+)',
        # Case Name v Case Name [Year] Court Number
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\[(\d{4})\]\s*([A-Z]{2,10})\s*(\d+)',
        # (Year) Court Number
        r'\((\d{4})\)\s*([A-Z]{2,10})\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            citation = match.group(0)
            
            # Extract context (surrounding text)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            citations.append((citation, context))
    
    return citations


def determine_citation_type(context: str) -> str:
    """
    Determine citation type: followed, distinguished, overruled, cited.
    """
    context_lower = context.lower()
    
    if any(word in context_lower for word in ['followed', 'applied', 'adopted', 'endorsed']):
        return 'followed'
    elif any(word in context_lower for word in ['distinguished', 'different', 'distinguishable']):
        return 'distinguished'
    elif any(word in context_lower for word in ['overruled', 'overturned', 'reversed']):
        return 'overruled'
    elif any(word in context_lower for word in ['cited', 'referenced', 'mentioned']):
        return 'cited'
    else:
        return 'cited'  # Default


def find_cited_cases_in_database(citation: str, cases_df: pd.DataFrame) -> Optional[str]:
    """
    Find if a citation matches a case in our database.
    Returns case_id if found.
    """
    # Normalize citation
    citation_clean = re.sub(r'[^\w\s\[\]()]', '', citation).strip()
    
    # Check against citations in database
    for _, row in cases_df.iterrows():
        db_citation = row.get('citation', '')
        if db_citation:
            db_citation_clean = re.sub(r'[^\w\s\[\]()]', '', db_citation).strip()
            
            # Check if citations match (fuzzy)
            if citation_clean.lower() in db_citation_clean.lower() or \
               db_citation_clean.lower() in citation_clean.lower():
                return row.get('case_id', '')
    
    return None


def analyze_precedents_with_gpt(judgment_text: str, known_cases: List[Dict]) -> List[Dict]:
    """
    Use GPT to identify precedent citations and their context.
    """
    if not HAS_OPENAI or not client:
        return []
    
    # Build list of known case citations
    known_citations = []
    for case in known_cases:
        citation = case.get('citation', '')
        case_id = case.get('case_id', '')
        case_name = case.get('case_name', '')
        if citation:
            known_citations.append(f"{citation} ({case_name}) - ID: {case_id}")
    
    known_citations_text = "\n".join(known_citations[:50])  # Limit to avoid token limits
    
    prompt = f"""Analyze this legal judgment text and identify citations to LGBTQ+ related cases.

Known LGBTQ+ cases in database:
{known_citations_text}

Judgment text (excerpt):
{judgment_text[:8000]}

Identify all citations to LGBTQ+ related cases and determine:
1. The citation
2. The case ID from the known cases list (if found)
3. The citation context (followed, distinguished, overruled, or just cited)
4. A brief description of how the case is being used

Return ONLY valid JSON array (no markdown):
[
    {{
        "citation": "citation text",
        "cited_case_id": "case_id if found in known cases, else empty string",
        "citation_type": "followed|distinguished|overruled|cited",
        "citation_context": "brief description of how case is cited"
    }}
]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
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
        
        precedents = json.loads(result_text)
        return precedents
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in precedent analysis: {e}")
        return []
    except Exception as e:
        logger.warning(f"GPT precedent analysis error: {e}")
        return []


def download_judgment_text(judgment_url: str) -> str:
    """Download and extract text from judgment URL."""
    if not judgment_url:
        return ""
    
    try:
        response = requests.get(judgment_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; PrecedentTracker/1.0)'
        })
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'pdf' in content_type or judgment_url.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    from io import BytesIO
                    
                    pdf_file = BytesIO(response.content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    text = ""
                    for page in pdf_reader.pages[:20]:  # First 20 pages
                        text += page.extract_text() + "\n"
                    
                    return text[:100000]  # Limit to 100k chars
                except Exception as e:
                    logger.warning(f"PDF extraction failed: {e}")
                    return ""
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator='\n', strip=True)
                return text[:100000]
        
    except Exception as e:
        logger.warning(f"Error downloading judgment: {e}")
    
    return ""


def load_existing_precedents() -> Set[Tuple[str, str]]:
    """Load existing precedent relationships."""
    existing = set()
    
    if PRECEDENTS_FILE.exists():
        try:
            df = pd.read_csv(PRECEDENTS_FILE)
            for _, row in df.iterrows():
                citing = row.get('citing_case_id', '')
                cited = row.get('cited_case_id', '')
                if citing and cited:
                    existing.add((citing, cited))
        except Exception as e:
            logger.warning(f"Error loading existing precedents: {e}")
    
    return existing


def save_precedents(precedents: List[Dict]):
    """Save precedent relationships to CSV."""
    if not precedents:
        return
    
    # Load existing precedents
    existing = load_existing_precedents()
    
    # Load existing file
    all_precedents = []
    if PRECEDENTS_FILE.exists():
        try:
            df = pd.read_csv(PRECEDENTS_FILE)
            all_precedents = df.to_dict('records')
        except:
            pass
    
    # Add new precedents
    for precedent in precedents:
        citing = precedent.get('citing_case_id', '')
        cited = precedent.get('cited_case_id', '')
        
        if citing and cited and (citing, cited) not in existing:
            all_precedents.append(precedent)
            existing.add((citing, cited))
    
    # Convert to DataFrame and save
    df = pd.DataFrame(all_precedents)
    
    # Ensure all required columns exist
    required_columns = [
        'citing_case_id', 'cited_case_id', 'citation_context',
        'citation_date', 'citation_type'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(PRECEDENTS_FILE, index=False)
    logger.info(f"Saved {len(df)} precedent relationships to {PRECEDENTS_FILE}")


def track_precedents() -> List[Dict]:
    """Track precedent citations for all cases."""
    if not CASES_FILE.exists():
        logger.warning(f"Cases file not found: {CASES_FILE}")
        return []
    
    # Load cases
    try:
        cases_df = pd.read_csv(CASES_FILE)
    except Exception as e:
        logger.error(f"Error loading cases: {e}")
        return []
    
    # Filter to LGBTQ+ relevant cases
    lgbtq_cases = cases_df[cases_df['lgbtq_relevance'].isin(['direct', 'indirect', 'affected'])].to_dict('records')
    
    # Load existing precedents
    existing = load_existing_precedents()
    
    # Track precedents
    all_precedents = []
    
    for idx, case_data in enumerate(lgbtq_cases, 1):
        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', '')
        judgment_url = case_data.get('full_judgment_url', '') or case_data.get('url', '')
        
        if not case_id or not judgment_url:
            continue
        
        logger.info(f"[{idx}/{len(lgbtq_cases)}] Tracking precedents: {case_name[:50]}...")
        
        # Download judgment text
        judgment_text = download_judgment_text(judgment_url)
        
        if not judgment_text:
            logger.warning(f"  Could not download judgment text")
            continue
        
        # Analyze with GPT
        precedents = analyze_precedents_with_gpt(judgment_text, lgbtq_cases)
        
        # Process precedents
        for precedent in precedents:
            cited_case_id = precedent.get('cited_case_id', '')
            
            if cited_case_id and (case_id, cited_case_id) not in existing:
                precedent_record = {
                    'citing_case_id': case_id,
                    'cited_case_id': cited_case_id,
                    'citation_context': precedent.get('citation_context', ''),
                    'citation_date': datetime.now().strftime('%Y-%m-%d'),
                    'citation_type': precedent.get('citation_type', 'cited')
                }
                
                all_precedents.append(precedent_record)
                logger.info(f"  ✓ Found precedent: {cited_case_id} ({precedent.get('citation_type', 'cited')})")
        
        # Rate limiting
        import time
        time.sleep(RATE_LIMIT_DELAY)
    
    return all_precedents


def main():
    """Main function."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Precedent Tracker")
    logger.info("=" * 60)
    
    precedents = track_precedents()
    
    if precedents:
        save_precedents(precedents)
        logger.info(f"\n✓ Tracked {len(precedents)} precedent relationships")
    else:
        logger.info("\n✓ No new precedents found")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

