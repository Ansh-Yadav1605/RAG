"""
Document Chunker Module — Mutual Fund FAQ Assistant

Splits raw scraped JSON documents into manageable chunks for embedding,
preserving metadata for each chunk.
"""

import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR

def chunk_documents(raw_docs: list[dict]) -> list[dict]:
    """
    Takes a list of raw documents (dicts) and returns a list of chunk dicts.
    """
    chunks = []
    
    # 300-500 tokens roughly translates to 1200-2000 characters
    # We will use character based splitting which is simpler and fast
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # ~350 tokens
        chunk_overlap=200, # ~50 tokens overlap
        length_function=len,
        separators=["\n\n", "\n", ". ", " | ", " ", ""]
    )
    
    chunk_counter = 1
    
    for doc in raw_docs:
        meta = doc.get("metadata", {})
        content = doc.get("content", {})
        
        if not meta or not content:
            continue
            
        scheme_id = meta.get("scheme_name", "unknown").split("–")[0].strip().replace(" ", "-").lower()
        
        # 1. First, create a high-density "Structured Facts" chunk
        # This guarantees that the most important facts are kept together and easily retrievable
        structured_text = f"Key Facts for {meta.get('scheme_name')}:\n"
        for key, val in content.items():
            if key != "Full Page Text" and val and val != "Not found":
                structured_text += f"- {key}: {val}\n"
                
        if len(structured_text) > 50:
            chunks.append({
                "chunk_id": f"{scheme_id}-facts-{chunk_counter}",
                "text": structured_text,
                "metadata": {
                    "source_url": meta.get("source_url"),
                    "scheme_name": meta.get("scheme_name"),
                    "category": meta.get("category"),
                    "scrape_date": meta.get("scrape_date"),
                    "section": "Key Facts"
                }
            })
            chunk_counter += 1
            
        # 2. Next, chunk the full page text to catch anything else
        full_text = content.get("Full Page Text", "")
        if len(full_text) > 100:
            text_chunks = text_splitter.split_text(full_text)
            for i, text_chunk in enumerate(text_chunks):
                # Skip tiny chunks that lack context
                if len(text_chunk.strip()) < 50:
                    continue
                    
                chunks.append({
                    "chunk_id": f"{scheme_id}-text-{chunk_counter}",
                    "text": f"Context for {meta.get('scheme_name')}:\n{text_chunk}",
                    "metadata": {
                        "source_url": meta.get("source_url"),
                        "scheme_name": meta.get("scheme_name"),
                        "category": meta.get("category"),
                        "scrape_date": meta.get("scrape_date"),
                        "section": "General Page Content"
                    }
                })
                chunk_counter += 1
                
    return chunks

def chunk_all():
    """Reads all raw JSON files, chunks them, and saves to processed/."""
    raw_docs = []
    
    # Read all raw JSON files
    for file_path in DATA_RAW_DIR.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                doc = json.load(f)
                raw_docs.append(doc)
            except json.JSONDecodeError:
                print(f"  [ERROR] Could not parse {file_path}")
                
    if not raw_docs:
        print("  [WARN] No raw documents found to chunk.")
        return []
        
    chunks = chunk_documents(raw_docs)
    
    # Save processed chunks
    output_path = DATA_PROCESSED_DIR / "chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
        
    print(f"  Created {len(chunks)} chunks and saved to {output_path.name}")
    return chunks

if __name__ == "__main__":
    chunk_all()
