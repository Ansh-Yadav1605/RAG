"""
Web Scraper Module — Mutual Fund FAQ Assistant

Fetches HTML from Groww scheme URLs, extracts structured factual text,
and attaches source metadata.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from pathlib import Path
from src.config import SCHEME_URLS, DATA_RAW_DIR

def extract_field_by_label(soup: BeautifulSoup, label: str) -> str | None:
    """
    Attempts to find a value next to or below a given label text.
    Groww usually has tables or label-value pairs for scheme details.
    """
    # Find all elements containing the label text (case-insensitive)
    elements = soup.find_all(string=re.compile(label, re.IGNORECASE))
    for el in elements:
        # Check parents/siblings for the corresponding value
        parent = el.parent
        
        # Pattern 1: Table row (th/td)
        tr = parent.find_parent("tr")
        if tr:
            cells = tr.find_all("td")
            if cells:
                return cells[-1].get_text(strip=True)
                
        # Pattern 2: Div structures where label and value are siblings or in a flexbox
        # Often it's a div containing a label div and a value div
        parent_div = parent.find_parent("div")
        if parent_div:
            # Let's just grab all text in the parent container that isn't the label
            # This is a bit brute force but works for many simple layouts.
            # A more targeted approach looks at siblings.
            siblings = list(parent_div.find_next_siblings("div"))
            if siblings:
                return siblings[0].get_text(strip=True)
                
            # If no sibling, maybe the value is just the next text element
            next_text = el.find_next(string=True)
            if next_text and next_text.strip() != "":
                return next_text.strip()
                
    return None

def extract_about_scheme(soup: BeautifulSoup) -> str:
    """Extracts general description or 'About' section."""
    about_headers = soup.find_all(string=re.compile(r"About\s+.*Fund", re.IGNORECASE))
    for header in about_headers:
        parent = header.parent
        # Look for a paragraph or div containing text nearby
        next_el = parent.find_next(["p", "div"])
        if next_el:
            return next_el.get_text(strip=True)
    return ""

def clean_text(text: str) -> str:
    """Removes excessive whitespace and newlines."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_scheme_page(scheme_info: dict) -> dict:
    """
    Scrapes a single Groww mutual fund page and returns structured data.
    """
    url = scheme_info["url"]
    name = scheme_info["name"]
    category = scheme_info["category"]
    
    print(f"Scraping: {name}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # We will dump all text chunks logically rather than strictly parsing every single field
    # perfectly, because RAG relies on text chunks. However, for structured data, we try.
    
    # Strategy for RAG: Extract the whole page text, but clean it up.
    # Groww pages have a lot of boilerplate. We want the main content.
    
    # Alternatively, build a structured dict that we will later chunk.
    # A structured dict guarantees we capture specific facts.
    
    data = {
        "metadata": {
            "source_url": url,
            "scheme_name": name,
            "category": category,
            "scrape_date": datetime.now().strftime("%Y-%m-%d")
        },
        "content": {}
    }
    
    # Try to extract key fields explicitly to ensure high quality
    fields_to_find = {
        "Expense Ratio": ["Expense Ratio", "TER"],
        "Exit Load": ["Exit Load"],
        "AUM": ["Fund Size", "AUM"],
        "Lock-in": ["Lock-in"],
        "Benchmark": ["Benchmark"],
        "Minimum SIP": ["Min. SIP", "Minimum SIP"],
        "Minimum Lumpsum": ["Min. Lumpsum", "Minimum Lumpsum"],
        "Risk": ["Risk"],
        "Fund Manager": ["Fund Manager", "Managed by"]
    }
    
    for field, labels in fields_to_find.items():
        found_val = None
        for label in labels:
            val = extract_field_by_label(soup, label)
            if val:
                found_val = val
                break
        data["content"][field] = clean_text(found_val) if found_val else "Not found"
        
    # Also grab general text from the main container to catch anything else
    # Groww usually puts content in a main wrapper or specific divs.
    # We'll just grab all text and let the chunker handle it as a fallback section.
    
    # Clean up scripts and styles
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
        
    full_text = soup.get_text(separator=" | ")
    full_text = clean_text(full_text)
    
    data["content"]["Full Page Text"] = full_text
    
    return data

def scrape_all():
    """Scrapes all configured schemes and saves to data/raw/."""
    results = []
    
    for scheme in SCHEME_URLS:
        data = scrape_scheme_page(scheme)
        if data:
            results.append(data)
            
            # Save to file
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', scheme["name"]).lower()
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            
            file_path = DATA_RAW_DIR / f"{safe_name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"  Saved raw data to {file_path.name}")
            
    return results

if __name__ == "__main__":
    scrape_all()
