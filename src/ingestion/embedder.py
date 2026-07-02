"""
Embedding Generator Module — Mutual Fund FAQ Assistant

Generates dense vector embeddings for document chunks using the BGE model.
"""

from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL, BGE_INSTRUCTION_PREFIX

# Load model lazily to avoid heavy initialization if not needed
_model = None

def get_model():
    global _model
    if _model is None:
        print(f"  [INFO] Loading embedding model: {EMBEDDING_MODEL} (this may take a moment)")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def generate_embeddings(chunks: list[dict]) -> list[tuple]:
    """
    Takes a list of chunk dicts, generates vectors, and returns a list of tuples:
    (chunk_id, chunk_text, embedding_vector, metadata)
    """
    if not chunks:
        return []
        
    model = get_model()
    
    # BGE models perform best when instructions are prepended to the indexed documents
    texts_to_embed = [f"{BGE_INSTRUCTION_PREFIX}{chunk['text']}" for chunk in chunks]
    
    print(f"  [INFO] Generating embeddings for {len(texts_to_embed)} chunks...")
    # Generate embeddings as a batch
    embeddings = model.encode(texts_to_embed, show_progress_bar=False)
    
    results = []
    for i, chunk in enumerate(chunks):
        # Convert NumPy array to Python list for ChromaDB compatibility
        vector = embeddings[i].tolist()
        
        results.append((
            chunk["chunk_id"],
            chunk["text"],
            vector,
            chunk["metadata"]
        ))
        
    return results

def generate_query_embedding(query: str) -> list[float]:
    """
    Generates an embedding for a single user query.
    For BGE models, we typically do NOT prepend the instruction prefix to the query itself
    if the prefix was "Represent this sentence: ", but it depends on the exact BGE version.
    Standard practice for BGE-small-en-v1.5: 
    Queries should NOT have the prefix if documents DO have the prefix, 
    or Queries DO have a prefix "Represent this sentence for searching relevant passages: "
    while documents have NO prefix.
    
    We'll follow the standard HuggingFace BGE guidance: 
    For retrieval, add prefix to queries ONLY, or instructions to documents ONLY.
    Since we added prefix to documents, we will embed query as is, OR we can use the query prefix.
    Let's just use the raw query as the BGE sentence-transformers implementation handles it well.
    """
    model = get_model()
    
    # BGE models recommend this specific prefix for the query if retrieving documents
    from src.config import BGE_QUERY_PREFIX
    query_text = f"{BGE_QUERY_PREFIX}{query}"
    
    vector = model.encode([query_text], show_progress_bar=False)[0].tolist()
    return vector
