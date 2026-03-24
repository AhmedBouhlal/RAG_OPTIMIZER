"""
Simple FastAPI Web Service for Universal RAG System
Clean, lightweight web service without complex production features
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from config import config
from logic import get_rag_system, OptimizedRAGSystem
from utils import RAGError, RetrievalError, GenerationError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG system instance
rag_system: Optional[OptimizedRAGSystem] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    try:
        logger.info("Initializing RAG System...")
        # Initialize the global RAG system
        await get_rag_system()
        logger.info("✅ RAG System initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down RAG System...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Universal RAG System",
    description="Simple RAG system for intelligent question answering",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    top_k: Optional[int] = Field(5, ge=1, le=50, description="Number of results to return")
    include_sources: Optional[bool] = Field(True, description="Include source document information")

class QueryResponse(BaseModel):
    query: str
    answer: str
    confidence_score: float
    source_documents: List[str]
    timestamp: str
    rag_analysis: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: str

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Universal RAG System",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Process a query using the RAG system

    - **query**: User question or query
    - **top_k**: Number of top results to return (1-50)
    - **include_sources**: Whether to include source document information
    """
    try:
        # Get the RAG system instance
        rag_system = await get_rag_system()

        if not rag_system or not rag_system._initialized:
            raise HTTPException(status_code=503, detail="RAG system not initialized")

        # Process query
        result = await rag_system.process_query(request.query)

        # Format response
        response = QueryResponse(
            query=result["query"],
            answer=result["answer"],
            confidence_score=result["confidence_score"],
            source_documents=result["source_documents"] if request.include_sources else [],
            timestamp=result["timestamp"],
            rag_analysis=result["rag_analysis"]
        )

        return response

    except RetrievalError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GenerationError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RAGError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint"""
    try:
        # Get the RAG system instance
        rag_system = await get_rag_system()
        status = "healthy" if rag_system and rag_system._initialized else "unhealthy"

        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            version="2.0.0"
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="2.0.0"
        )

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "chunk_size": config.chunk_size,
        "overlap": config.overlap,
        "top_k": config.top_k,
        "vector_weight": config.vector_weight,
        "keyword_weight": config.keyword_weight,
        "embedding_model": config.embedding_model,
        "reranker_model": config.reranker_model,
        "ollama_model": config.ollama_model
    }

# Exception handlers
@app.exception_handler(RAGError)
async def rag_error_handler(request, exc: RAGError):
    """Handle RAG system errors"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="RAG System Error",
            message=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Run the service
if __name__ == "__main__":
    uvicorn.run(
        "web_service:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level=config.log_level.lower()
    )
