#!/usr/bin/env python3
"""
Legislative Linkage
==================
Links legal cases to relevant legislation:
- Which laws are being challenged/interpreted in cases
- Whether cases support or oppose specific legislation
- Cases that led to legislative change
- Cross-reference between legal cases and parliamentary bills
"""

import os
import sys
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

import pandas as pd

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
BILLS_FILE = DATA_DIR / "parliamentary-bills.csv"
POLICY_FILE = DATA_DIR / "policy-landscape.csv"
LINKAGE_FILE = DATA_DIR / "case-bill-linkage.csv"

logger = logging.getLogger(__name__)


def setup_logging():
    """Setup logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def extract_legislation_references(text: str) -> List[str]:
    """Extract references to legislation from text."""
    legislation = []
    
    # Common patterns for legislation references
    patterns = [
        # Act names: "Sex Discrimination Act", "Marriage Act 1961"
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Act(?:\s+\d{4})?',
        # Section references: "s 5", "section 5", "s.5"
        r'[Ss]ection\s+(\d+[A-Z]?)|[Ss]\.?\s*(\d+[A-Z]?)',
        # Regulation references
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Regulations(?:\s+\d{4})?',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            legislation.append(match.group(0))
    
    return list(set(legislation))  # Remove duplicates


def link_case_to_bills_with_gpt(case_data: Dict, bills: List[Dict]) -> List[Dict]:
    """
    Use GPT to identify which bills are related to a case.
    """
    if not HAS_OPENAI or not client:
        return []
    
    case_name = case_data.get('case_name', '')
    case_summary = case_data.get('case_summary', '')
    case_type = case_data.get('case_type', '')
    
    # Build bills list
    bills_text = ""
    for bill in bills[:20]:  # Limit to avoid token limits
        bill_id = bill.get('bill_id', '')
        title = bill.get('title', '')
        keywords = bill.get('keywords_matched', '')
        bills_text += f"- {bill_id}: {title} (Keywords: {keywords})\n"
    
    prompt = f"""Analyze this legal case and identify which parliamentary bills are related to it.

Case: {case_name}
Type: {case_type}
Summary: {case_summary}

Available Bills:
{bills_text}

Identify which bills are:
1. Directly related (challenged, interpreted, or affected by this case)
2. Indirectly related (same policy area or topic)

For each related bill, determine:
- bill_id
- relationship_type: "challenged" | "interpreted" | "supports" | "opposes" | "related"
- relationship_description: brief explanation

Return ONLY valid JSON array (no markdown):
[
    {{
        "bill_id": "bill_id",
        "relationship_type": "challenged|interpreted|supports|opposes|related",
        "relationship_description": "brief explanation"
    }}
]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800,
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
        
        linkages = json.loads(result_text)
        return linkages
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in linkage analysis: {e}")
        return []
    except Exception as e:
        logger.warning(f"GPT linkage analysis error: {e}")
        return []


def update_policy_landscape(case_data: Dict, linkages: List[Dict]):
    """Update policy landscape based on case outcomes."""
    if not POLICY_FILE.exists():
        return
    
    try:
        df = pd.read_csv(POLICY_FILE)
    except Exception as e:
        logger.warning(f"Error loading policy landscape: {e}")
        return
    
    case_outcome = case_data.get('outcome', '').lower()
    case_sentiment = case_data.get('sentiment', '').lower()
    
    # Update policies related to linked bills
    for linkage in linkages:
        bill_id = linkage.get('bill_id', '')
        relationship = linkage.get('relationship_type', '')
        
        # Find policies related to this bill
        for idx, policy in df.iterrows():
            related_bills = policy.get('related_bills', '')
            if bill_id in str(related_bills):
                # Update policy status based on case outcome
                if case_outcome == 'won' and case_sentiment == 'positive':
                    # Positive case outcome might support policy
                    df.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
                elif case_outcome == 'lost' and case_sentiment == 'negative':
                    # Negative case outcome might challenge policy
                    df.at[idx, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    df.to_csv(POLICY_FILE, index=False)
    logger.info("Updated policy landscape")


def load_existing_linkages() -> Set[Tuple[str, str]]:
    """Load existing case-bill linkages."""
    existing = set()
    
    if LINKAGE_FILE.exists():
        try:
            df = pd.read_csv(LINKAGE_FILE)
            for _, row in df.iterrows():
                case_id = row.get('case_id', '')
                bill_id = row.get('bill_id', '')
                if case_id and bill_id:
                    existing.add((case_id, bill_id))
        except Exception as e:
            logger.warning(f"Error loading existing linkages: {e}")
    
    return existing


def save_linkages(linkages: List[Dict]):
    """Save case-bill linkages to CSV."""
    if not linkages:
        return
    
    # Load existing linkages
    existing = load_existing_linkages()
    
    # Load existing file
    all_linkages = []
    if LINKAGE_FILE.exists():
        try:
            df = pd.read_csv(LINKAGE_FILE)
            all_linkages = df.to_dict('records')
        except:
            pass
    
    # Add new linkages
    for linkage in linkages:
        case_id = linkage.get('case_id', '')
        bill_id = linkage.get('bill_id', '')
        
        if case_id and bill_id and (case_id, bill_id) not in existing:
            all_linkages.append(linkage)
            existing.add((case_id, bill_id))
    
    # Convert to DataFrame and save
    df = pd.DataFrame(all_linkages)
    
    # Ensure all required columns exist
    required_columns = [
        'case_id', 'bill_id', 'relationship_type', 'relationship_description',
        'linkage_date'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns
    df = df[required_columns]
    
    df.to_csv(LINKAGE_FILE, index=False)
    logger.info(f"Saved {len(df)} case-bill linkages to {LINKAGE_FILE}")


def link_cases_to_bills() -> List[Dict]:
    """Link cases to parliamentary bills."""
    if not CASES_FILE.exists():
        logger.warning(f"Cases file not found: {CASES_FILE}")
        return []
    
    if not BILLS_FILE.exists():
        logger.warning(f"Bills file not found: {BILLS_FILE}")
        return []
    
    # Load cases
    try:
        cases_df = pd.read_csv(CASES_FILE)
    except Exception as e:
        logger.error(f"Error loading cases: {e}")
        return []
    
    # Load bills
    try:
        bills_df = pd.read_csv(BILLS_FILE)
    except Exception as e:
        logger.error(f"Error loading bills: {e}")
        return []
    
    # Filter to LGBTQ+ relevant cases
    lgbtq_cases = cases_df[cases_df['lgbtq_relevance'].isin(['direct', 'indirect', 'affected'])].to_dict('records')
    bills = bills_df.to_dict('records')
    
    # Load existing linkages
    existing = load_existing_linkages()
    
    # Link cases to bills
    all_linkages = []
    
    for idx, case_data in enumerate(lgbtq_cases, 1):
        case_id = case_data.get('case_id', '')
        case_name = case_data.get('case_name', '')
        
        if not case_id:
            continue
        
        logger.info(f"[{idx}/{len(lgbtq_cases)}] Linking: {case_name[:50]}...")
        
        # Use GPT to identify related bills
        linkages = link_case_to_bills_with_gpt(case_data, bills)
        
        # Process linkages
        for linkage in linkages:
            bill_id = linkage.get('bill_id', '')
            
            if bill_id and (case_id, bill_id) not in existing:
                linkage_record = {
                    'case_id': case_id,
                    'bill_id': bill_id,
                    'relationship_type': linkage.get('relationship_type', 'related'),
                    'relationship_description': linkage.get('relationship_description', ''),
                    'linkage_date': datetime.now().strftime('%Y-%m-%d')
                }
                
                all_linkages.append(linkage_record)
                logger.info(f"  ✓ Linked to bill: {bill_id} ({linkage.get('relationship_type', 'related')})")
        
        # Update policy landscape
        if linkages:
            update_policy_landscape(case_data, linkages)
        
        # Rate limiting
        import time
        time.sleep(RATE_LIMIT_DELAY)
    
    return all_linkages


def main():
    """Main function."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Legislative Linkage")
    logger.info("=" * 60)
    
    linkages = link_cases_to_bills()
    
    if linkages:
        save_linkages(linkages)
        logger.info(f"\n✓ Created {len(linkages)} case-bill linkages")
    else:
        logger.info("\n✓ No new linkages found")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

