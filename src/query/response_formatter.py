"""
Response Formatter Module — Mutual Fund FAQ Assistant

Formats the raw LLM output into a strict structured JSON response,
enforcing length limits and citation rules.
"""

import re
from datetime import datetime

def extract_url(text: str) -> str | None:
    """Finds the first URL in a string."""
    match = re.search(r'(https?://[^\s]+)', text)
    if match:
        # Strip trailing punctuation if accidentally captured
        url = match.group(1).rstrip('.,;)')
        return url
    return None

def enforce_three_sentences(text: str) -> str:
    """Truncates text to a maximum of 3 sentences."""
    # Split by common sentence delimiters (., !, ?)
    # Keeping the delimiter attached to the sentence
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    if len(sentences) <= 3:
        return text.strip()
        
    return " ".join(sentences[:3]).strip()

def format_response(llm_answer: str, retrieved_chunks: list[dict], intent: str = "FACTUAL") -> dict:
    """
    Takes the raw LLM output and top chunks, enforcing:
    - Max 3 sentences
    - Exactly 1 citation URL
    - "Last updated" footer
    """
    # 1. Enforce length limit
    answer_text = enforce_three_sentences(llm_answer)
    
    # 2. Extract/Enforce URL
    # If the LLM didn't include a URL, grab it from the top chunk
    url = extract_url(answer_text)
    
    # Remove all URLs from the answer text to keep it clean, we'll return it in the structured data
    # (or we can just leave it if we want the frontend to render it inline, 
    # but the problem statement says "every response must include a SINGLE clear source link".
    # It's cleaner to return it as a structured field and let frontend render it).
    clean_answer = re.sub(r'https?://[^\s]+', '', answer_text).strip()
    
    if not url and retrieved_chunks:
        url = retrieved_chunks[0]["metadata"].get("source_url")
        
    # If no info found response
    if "don't have that information" in clean_answer.lower():
        url = None # Don't cite a source if we didn't find the answer
        scheme_name = None
    else:
        scheme_name = retrieved_chunks[0]["metadata"].get("scheme_name") if retrieved_chunks else None
        
    last_updated = datetime.now().strftime("%Y-%m-%d")
    
    # We won't append the "Last updated" directly to the text string here, 
    # it's better returned as a structured field and assembled by the frontend.
    # But if the requirement meant literally appending it to the string:
    # "footer: 'Last updated from sources: <date>'"
    # We will provide it as a structured field for the frontend to render.
    
    return {
        "status": "success",
        "data": {
            "answer": clean_answer,
            "source_url": url,
            "last_updated": last_updated,
            "intent": intent,
            "scheme": scheme_name
        }
    }
