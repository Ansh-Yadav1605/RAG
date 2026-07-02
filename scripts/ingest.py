#!/usr/bin/env python3
"""
Ingestion CLI Script — Mutual Fund FAQ Assistant

Orchestrates the entire ingestion pipeline:
1. Scrape the 5 Groww URLs
2. Chunk the raw text
3. Generate BGE embeddings
4. Store in ChromaDB
"""

import sys
from pathlib import Path
import time

# Ensure src is in the python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ingestion.scraper import scrape_all
from src.ingestion.chunker import chunk_all
from src.ingestion.embedder import generate_embeddings
from src.ingestion.vector_store import clear_collection, index_chunks, get_collection_stats

def main():
    start_time = time.time()
    print("=" * 60)
    print("Starting Data Ingestion Pipeline")
    print("=" * 60)
    
    # Step 1: Scrape
    print("\n[Step 1/4] Scraping data from Groww...")
    raw_docs = scrape_all()
    if not raw_docs:
        print("[ERROR] Scraper returned no data. Aborting.")
        sys.exit(1)
        
    # Step 2: Chunk
    print("\n[Step 2/4] Chunking documents...")
    # chunk_all reads from data/raw/ directly
    chunks = chunk_all()
    if not chunks:
        print("[ERROR] Chunker produced no chunks. Aborting.")
        sys.exit(1)
        
    # Step 3: Embed
    print("\n[Step 3/4] Generating BGE embeddings...")
    chunks_with_embeddings = generate_embeddings(chunks)
    if not chunks_with_embeddings:
        print("[ERROR] Embedder produced no embeddings. Aborting.")
        sys.exit(1)
        
    # Step 4: Store
    print("\n[Step 4/4] Storing vectors in ChromaDB...")
    clear_collection() # Ensure we don't duplicate
    index_chunks(chunks_with_embeddings)
    
    # Final Summary
    stats = get_collection_stats()
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print(f"   Pages scraped   : {len(raw_docs)}")
    print(f"   Chunks created  : {len(chunks)}")
    print(f"   Vectors indexed : {stats['count']}")
    print(f"   Time elapsed    : {elapsed:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    main()
