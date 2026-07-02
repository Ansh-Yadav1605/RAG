"""
LLM Client Module — Mutual Fund FAQ Assistant

Handles communication with the Groq API, incorporating retry logic
for rate limits and fallbacks.
"""

import os
from groq import Groq, APIError, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from src.config import GROQ_API_KEY, LLM_MODEL, LLM_FALLBACK_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

# Initialize client globally
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set.")
    
_client = Groq(api_key=GROQ_API_KEY)

# We use tenacity to handle Groq rate limits (30 RPM, 1K RPD, 12K TPM).
# Exponential backoff: wait 2^x * 1 second between each retry, max 3 attempts
@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)
def _call_groq_with_retry(messages: list, model: str, max_tokens: int) -> str:
    """Internal function to call Groq with automatic retries on rate limits."""
    completion = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=LLM_TEMPERATURE,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content

def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = LLM_MAX_TOKENS) -> str:
    """
    Calls the Groq LLM with a system and user prompt.
    Falls back to a secondary model if the primary model fails after retries.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Try primary model first (llama-3.3-70b-versatile)
        return _call_groq_with_retry(messages, LLM_MODEL, max_tokens)
    except RateLimitError:
        print(f"[WARN] Primary model {LLM_MODEL} rate limited. Falling back to {LLM_FALLBACK_MODEL}.")
        try:
            # Try fallback model if rate limit persists
            return _call_groq_with_retry(messages, LLM_FALLBACK_MODEL, max_tokens)
        except Exception as e:
            print(f"[ERROR] Fallback model also failed: {e}")
            raise RuntimeError("LLM Service is currently unavailable due to rate limits.") from e
    except APIError as e:
        print(f"[ERROR] Groq API Error: {e}")
        raise RuntimeError(f"LLM API Error: {e}") from e
    except Exception as e:
        print(f"[ERROR] Unexpected LLM error: {e}")
        raise
