#!/usr/bin/env python3
"""
Verify Embeddings Script
Utility script to verify that embeddings were correctly generated and stored in ChromaDB.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ingestion.vector_store import get_collection

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        collection = get_collection()
        count = collection.count()
        print("=" * 80)
        print(f"Connection successful. Total chunks in ChromaDB: {count}")
        print("=" * 80)
        
        if count == 0:
            print("Vector store is empty! Run ingest.py first.")
            return

        # Fetch up to 5 items to inspect
        results = collection.get(include=["documents", "embeddings", "metadatas"], limit=5)
        
        ids = results.get("ids", [])
        documents = results.get("documents", [])
        embeddings = results.get("embeddings", [])
        metadatas = results.get("metadatas", [])
        
        for i in range(len(ids)):
            print(f"\n[{i+1}] Chunk ID: {ids[i]}")
            print(f"    Scheme: {metadatas[i].get('scheme_name')}")
            print(f"    Category: {metadatas[i].get('category')}")
            
            # Print a snippet of the document
            doc_snippet = documents[i].replace("\n", " ")[:150]
            print(f"    Text: {doc_snippet}...")
            
            # Print first 5 dimensions of the embedding
            if len(embeddings) > i and embeddings[i] is not None and len(embeddings[i]) > 0:
                emb = embeddings[i]
                print(f"    Embedding Dimensions: {len(emb)}")
                print(f"    Embedding Prefix: {emb[:5]} ...")
            else:
                print("    [WARNING] No embedding found for this chunk!")
                
        print("\n" + "=" * 80)
        print("Embeddings verification complete.")
        
    except Exception as e:
        print(f"[ERROR] Failed to connect to ChromaDB or retrieve data: {e}")

if __name__ == "__main__":
    main()
