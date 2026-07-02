"""
Intent Classifier Module — Mutual Fund FAQ Assistant

Classifies user queries into three categories: FACTUAL, ADVISORY, or OUT_OF_SCOPE.
Also performs early PII detection and rejection.
"""

import re
from src.config import PII_PATTERNS, ADVISORY_KEYWORDS
from src.query.llm_client import call_llm

def detect_pii(query: str) -> bool:
    """Returns True if any PII pattern matches the query."""
    for pattern in PII_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def detect_advisory_keywords(query: str) -> bool:
    """Fast-path detection of obvious advisory queries."""
    query_lower = query.lower()
    for keyword in ADVISORY_KEYWORDS:
        # Check for whole word match to avoid substring false positives
        if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
            return True
    return False

def classify_intent(query: str) -> str:
    """
    Returns one of: 'FACTUAL', 'ADVISORY', or 'OUT_OF_SCOPE'
    """
    if not query or not query.strip():
        return "OUT_OF_SCOPE"
        
    # 1. Hard block on PII
    if detect_pii(query):
        return "ADVISORY" # Treat PII requests as policy violations needing refusal
        
    # 2. Fast-path heuristic for advisory
    if detect_advisory_keywords(query):
        return "ADVISORY"
        
    # 3. LLM-based classification for nuance
    system_prompt = """You are an intent classifier for a Mutual Fund FAQ bot.
Analyze the user's query and classify it into EXACTLY ONE of these three categories:
1. "FACTUAL": The user is asking an objective question about mutual fund details (e.g. expense ratio, NAV, exit load, fund manager, AUM, minimum investment).
2. "ADVISORY": The user is asking for financial advice, recommendations, predictions, comparisons, or asking if they "should" invest.
3. "OUT_OF_SCOPE": The user is asking about something completely unrelated to mutual funds (e.g. weather, sports, banking, crypto).

Respond with ONLY the category name (FACTUAL, ADVISORY, or OUT_OF_SCOPE) and nothing else.
"""
    
    # We use a very low max_tokens for classification
    try:
        response = call_llm(system_prompt, query, max_tokens=10)
        result = response.strip().upper()
        
        # Clean up any potential markdown or punctuation
        result = re.sub(r'[^A-Z_]', '', result)
        
        if result in ["FACTUAL", "ADVISORY", "OUT_OF_SCOPE"]:
            return result
            
        # Fallback if LLM gives weird output
        return "ADVISORY"
        
    except Exception as e:
        print(f"[ERROR] Intent classification failed: {e}")
        # Fail safe
        return "ADVISORY"
