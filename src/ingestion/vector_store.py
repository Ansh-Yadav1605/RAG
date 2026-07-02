"""
Vector Store Module — Mutual Fund FAQ Assistant

Manages persistent connection to ChromaDB. Supports indexing, clearing,
and querying document embeddings.
"""

import chromadb
from chromadb.config import Settings
from src.config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME

# Initialize ChromaDB client globally
_client = None
_collection = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
    return _client

def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )
    return _collection

def clear_collection():
    """Deletes all data in the collection."""
    client = get_client()
    try:
        client.delete_collection(name=CHROMA_COLLECTION_NAME)
        global _collection
        _collection = None
        print(f"  [INFO] Cleared collection '{CHROMA_COLLECTION_NAME}'")
    except Exception:
        # Collection might not exist yet
        pass

def index_chunks(chunks_with_embeddings: list[tuple]):
    """
    Upserts chunks and their embeddings into ChromaDB.
    Input format: list of (chunk_id, chunk_text, embedding_vector, metadata)
    """
    if not chunks_with_embeddings:
        return
        
    collection = get_collection()
    
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for item in chunks_with_embeddings:
        chunk_id, text, vector, meta = item
        ids.append(chunk_id)
        documents.append(text)
        embeddings.append(vector)
        metadatas.append(meta)
        
    # ChromaDB supports batching naturally, but if the list was huge, 
    # we'd want to chunk the upsert calls. 5 schemes is small enough.
    print(f"  [INFO] Upserting {len(ids)} chunks to ChromaDB...")
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

def get_collection_stats() -> dict:
    """Returns statistics about the vector store."""
    try:
        collection = get_collection()
        count = collection.count()
        return {"count": count}
    except Exception:
        return {"count": 0}
