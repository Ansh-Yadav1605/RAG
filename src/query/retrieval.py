"""
Retrieval Module — Mutual Fund FAQ Assistant

Handles querying the ChromaDB vector store using BGE embeddings.
"""

from src.ingestion.embedder import generate_query_embedding
from src.ingestion.vector_store import get_collection
from src.config import TOP_K, SIMILARITY_THRESHOLD

def retrieve_chunks(query: str, top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD) -> list[dict]:
    """
    Retrieves the most relevant chunks from ChromaDB for a given query.
    Returns a list of dictionaries with text, metadata, and distance.
    """
    # 1. Embed the query
    query_vector = generate_query_embedding(query)
    
    # 2. Query the collection
    collection = get_collection()
    
    try:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        return []
        
    if not results or not results["documents"] or not results["documents"][0]:
        return []
        
    retrieved = []
    
    # Extract the first list of results (since we only queried 1 vector)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    for i in range(len(documents)):
        # ChromaDB distance with cosine metric: lower is more similar (1 - cosine_similarity)
        # So distance 0 = exact match. 
        # A distance threshold of 0.35 means similarity >= 0.65
        distance = distances[i]
        
        # BGE models use cosine similarity.
        # Let's say SIMILARITY_THRESHOLD = 0.65
        # 1 - 0.65 = 0.35 distance
        max_distance = 1.0 - threshold
        
        if distance <= max_distance:
            retrieved.append({
                "text": documents[i],
                "metadata": metadatas[i],
                "distance": distance
            })
            
    return retrieved
