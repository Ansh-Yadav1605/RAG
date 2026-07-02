"""
Pydantic Models Module — FastAPI Backend

Defines the request and response schemas for the API endpoints.
"""

from pydantic import BaseModel, Field, constr
from typing import Optional

# ------------------------------------------------------------
# API Request Models
# ------------------------------------------------------------

class QueryRequest(BaseModel):
    """
    Request payload for the /ask endpoint.
    Restricts query length to max 500 characters to prevent abuse.
    """
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=500,
        description="The mutual fund question from the user."
    )

# ------------------------------------------------------------
# API Response Models
# ------------------------------------------------------------

class QueryResponseData(BaseModel):
    """
    The nested data payload for a successful or refused query.
    """
    answer: str
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    intent: str
    scheme: Optional[str] = None

class QueryResponse(BaseModel):
    """
    Main response schema for the /ask endpoint.
    Status can be 'success', 'refused', or 'error'.
    """
    status: str
    data: Optional[QueryResponseData] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """
    Response schema for the /health endpoint.
    """
    status: str
    vector_store_chunks: int
    last_ingestion: Optional[str] = None
