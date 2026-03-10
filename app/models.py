from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UploadResponse(BaseModel):
    status: str
    filename: str
    doc_id: str
    chunks: Optional[int] = 0
    message: Optional[str] = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    return_sources: bool = True

class QueryResponse(BaseModel):
    answer: str
    source_documents: Optional[List[Dict[str, Any]]] = None

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    last_update: str

class HealthCheck(BaseModel):
    status: str
    app: str
    documents: int
