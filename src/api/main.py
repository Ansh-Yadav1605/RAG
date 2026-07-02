"""
Main FastAPI Application Module — Mutual Fund FAQ Assistant

Exposes the RAG pipeline as a REST API with /ask and /health endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from datetime import datetime

from src.api.models import QueryRequest, QueryResponse, HealthResponse
from src.query.intent_classifier import classify_intent
from src.query.retrieval import retrieve_chunks
from src.query.prompt_builder import build_prompt
from src.query.llm_client import call_llm
from src.query.response_formatter import format_response
from src.query.refusal_handler import generate_refusal
from src.ingestion.vector_store import get_collection_stats, get_collection

# ------------------------------------------------------------
# Application Setup
# ------------------------------------------------------------

app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="RAG-based API for objective mutual fund queries.",
    version="1.0.0"
)

# Allow frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Lifecycle Events
# ------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Load necessary resources on startup to prevent latency on first request."""
    print("Starting FastAPI Server for Mutual Fund FAQ Assistant")
    # Wake up the ChromaDB connection
    try:
        get_collection()
        print("Vector store connection initialized.")
    except Exception as e:
        print(f"⚠️ Vector store initialization failed (might be empty): {e}")

# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Returns system health and vector store statistics.
    """
    stats = get_collection_stats()
    
    # We use a placeholder for last_ingestion.
    # In a real system, we might query the latest 'scrape_date' from metadata.
    return HealthResponse(
        status="healthy",
        vector_store_chunks=stats.get("count", 0),
        last_ingestion=datetime.now().strftime("%Y-%m-%d")
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Main endpoint for answering mutual fund questions.
    Follows the RAG pipeline: Classify -> Retrieve -> Prompt -> LLM -> Format
    """
    try:
        q = request.query.strip()
        
        # 1. Classify Intent
        intent = classify_intent(q)
        
        # 2. Early Exit for Non-Factual
        if intent != "FACTUAL":
            refusal_dict = generate_refusal(q, intent)
            return QueryResponse(
                status=refusal_dict["status"],
                data=refusal_dict["data"]
            )
            
        # 3. Retrieve Context
        chunks = retrieve_chunks(q)
        
        # If no chunks meet the similarity threshold, we still call the LLM 
        # but with empty context, and the system prompt will force it to refuse.
        # Alternatively, we could fail early here, but the LLM provides a softer "I don't know".
        
        # 4. Build Prompt
        sys_prompt, user_prompt = build_prompt(q, chunks)
        
        # 5. Call LLM
        ans = call_llm(sys_prompt, user_prompt)
        
        # 6. Format Final Output
        res_dict = format_response(ans, chunks, intent)
        
        return QueryResponse(
            status=res_dict["status"],
            data=res_dict["data"]
        )
        
    except Exception as e:
        print(f"[ERROR] /ask endpoint failed: {e}")
        # Return a 500 error gracefully
        raise HTTPException(status_code=500, detail="Internal server error while processing query.")
