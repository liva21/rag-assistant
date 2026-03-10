from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from loguru import logger

from app.models import (
    UploadResponse, 
    QueryRequest, 
    QueryResponse, 
    StatsResponse
)
from app.config import get_settings
from src.rag_engine import RAGEngine

settings = get_settings()
router = APIRouter()

# RAG Engine instance (singleton)
rag_engine = RAGEngine()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Desteklenmeyen format: {file_ext}")
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(status_code=400, detail="Dosya çok büyük")
        
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📁 Dosya kaydedildi: {file_path}")
        result = rag_engine.ingest_document(str(file_path))
        return UploadResponse(**result)
    except Exception as e:
        logger.error(f"Upload hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        result = rag_engine.query(request.question, request.top_k, request.return_sources)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    doc_count = 0
    if rag_engine.vector_store is not None:
        try:
            # FAISS vector store'da ntotal ile toplam vektör sayısını alıyoruz
            doc_count = rag_engine.vector_store.index.ntotal
        except Exception:
            doc_count = 0
    return {"status": "healthy", "app": settings.APP_NAME, "documents": doc_count}
