"""
Refusal Handler Module — Mutual Fund FAQ Assistant

Generates polite, compliant refusals for advisory or out-of-scope queries.
"""

from src.config import REFUSAL_LINKS

def generate_refusal(query: str, intent: str) -> dict:
    """
    Returns a standard, structured dictionary for a refused query.
    """
    if intent == "ADVISORY":
        msg = (
            "I'm unable to provide investment advice, performance comparisons, "
            "or recommendations. I can only provide factual details about mutual fund schemes."
        )
        url = REFUSAL_LINKS["ADVISORY"]
        
    elif intent == "OUT_OF_SCOPE":
        msg = (
            "I can only answer questions related to mutual fund schemes. "
            "For general financial education, please refer to official resources."
        )
        url = REFUSAL_LINKS["OUT_OF_SCOPE"]
        
    else:
        # Fallback for unexpected intents
        msg = "I'm unable to process this request."
        url = REFUSAL_LINKS["OUT_OF_SCOPE"]
        
    return {
        "status": "refused",
        "data": {
            "answer": msg,
            "source_url": url,
            "last_updated": None,
            "intent": intent,
            "scheme": None
        }
    }
