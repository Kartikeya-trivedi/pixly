"""
Health check router.
Provides basic health and status endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.db.database import get_db
from src.services.rag_service import RAGService

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "Game Overlay AI",
        "version": "1.0.0"
    }


@router.get("/status")
async def status_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed status check including database connectivity."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Test RAG service
    try:
        rag_service = RAGService()
        rag_status = "available"
    except Exception as e:
        rag_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "rag_service": rag_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }
