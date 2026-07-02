"""
Mutual Fund FAQ Assistant — Configuration Module

Loads environment variables from .env and exposes all project-wide
constants including Groq settings, embedding model config, retrieval
parameters, and the 5 HDFC Mutual Fund scheme URLs from Groww.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# Python Version Check
# ============================================================
if sys.version_info < (3, 10):
    raise RuntimeError(
        f"Python 3.10+ is required. You are running Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# ============================================================
# Load .env file
# ============================================================
# Resolve project root (two levels up from src/config.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    print(f"⚠️  Warning: .env file not found at {ENV_PATH}. Using environment variables or defaults.")

# ============================================================
# Groq LLM Configuration
# ============================================================
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_FALLBACK_MODEL: str = "mixtral-8x7b-32768"
LLM_TEMPERATURE: float = 0.0
LLM_MAX_TOKENS: int = 200

if not GROQ_API_KEY:
    raise EnvironmentError(
        "Missing required env var: GROQ_API_KEY. "
        "Copy .env.example to .env and set your Groq API key."
    )

# ============================================================
# Embedding Model Configuration
# ============================================================
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_DIMENSIONS: int = 384  # BGE-small-en-v1.5 output size
BGE_INSTRUCTION_PREFIX: str = "Represent this sentence: "
BGE_QUERY_PREFIX: str = "Represent this sentence for searching relevant passages: "

# ============================================================
# ChromaDB Vector Store Configuration
# ============================================================
CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", str(PROJECT_ROOT / "vectorstore" / "chroma_db"))
CHROMA_COLLECTION_NAME: str = "mutual_fund_faq"

# ============================================================
# Retrieval Parameters
# ============================================================
TOP_K: int = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))

# ============================================================
# API Configuration
# ============================================================
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000
MAX_QUERY_LENGTH: int = 500

# ============================================================
# Scheme URLs — Primary Data Sources (Groww)
# ============================================================
SCHEME_URLS: list[dict[str, str]] = [
    {
        "name": "HDFC Large Cap Fund – Direct Plan – Growth",
        "category": "Large Cap",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    },
    {
        "name": "HDFC Mid-Cap Opportunities Fund – Direct Plan – Growth",
        "category": "Mid Cap",
        "url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    },
    {
        "name": "HDFC Small Cap Fund – Direct Plan – Growth",
        "category": "Small Cap",
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    },
    {
        "name": "HDFC Gold ETF Fund of Fund – Direct Plan – Growth",
        "category": "Gold ETF FoF",
        "url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    },
    {
        "name": "HDFC Silver ETF Fund of Fund – Direct Plan – Growth",
        "category": "Silver ETF FoF",
        "url": "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    },
]

# ============================================================
# Advisory / Refusal Keywords
# ============================================================
ADVISORY_KEYWORDS: list[str] = [
    "should", "better", "recommend", "compare", "worth",
    "invest", "suggest", "prefer", "which one", "good fund",
    "best fund", "switch", "buy", "sell", "prediction",
    "forecast", "will it", "grow", "return", "profit",
]

# ============================================================
# Refusal Redirect Links (NOT corpus sources)
# ============================================================
REFUSAL_LINKS: dict[str, str] = {
    "ADVISORY": "https://investor.sebi.gov.in/",
    "OUT_OF_SCOPE": "https://www.amfiindia.com/investor-corner/knowledge-center.html",
}

# ============================================================
# PII Detection Patterns
# ============================================================
PII_PATTERNS: list[str] = [
    r"[A-Z]{5}[0-9]{4}[A-Z]",          # PAN
    r"\b\d{4}\s?\d{4}\s?\d{4}\b",       # Aadhaar
    r"\b\d{10}\b",                       # Phone number
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # Email
]

# ============================================================
# Data Paths
# ============================================================
DATA_RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"

# Ensure data directories exist
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
