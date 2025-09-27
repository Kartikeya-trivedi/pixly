"""
Custom exceptions for the Game Overlay AI application.
Defines application-specific error handling.
"""

from fastapi import HTTPException
from typing import Any, Dict, Optional


class GameOverlayException(Exception):
    """Base exception for Game Overlay AI application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RAGServiceException(GameOverlayException):
    """Exception raised by RAG service operations."""
    pass


class ETLServiceException(GameOverlayException):
    """Exception raised by ETL service operations."""
    pass


class AgentServiceException(GameOverlayException):
    """Exception raised by agent service operations."""
    pass


class OverlayServiceException(GameOverlayException):
    """Exception raised by overlay service operations."""
    pass


class DatabaseException(GameOverlayException):
    """Exception raised by database operations."""
    pass


def handle_rag_exception(e: Exception) -> HTTPException:
    """Convert RAG service exception to HTTP exception."""
    if isinstance(e, RAGServiceException):
        return HTTPException(status_code=503, detail=f"RAG service error: {e.message}")
    return HTTPException(status_code=500, detail="Internal RAG service error")


def handle_etl_exception(e: Exception) -> HTTPException:
    """Convert ETL service exception to HTTP exception."""
    if isinstance(e, ETLServiceException):
        return HTTPException(status_code=503, detail=f"ETL service error: {e.message}")
    return HTTPException(status_code=500, detail="Internal ETL service error")


def handle_agent_exception(e: Exception) -> HTTPException:
    """Convert agent service exception to HTTP exception."""
    if isinstance(e, AgentServiceException):
        return HTTPException(status_code=503, detail=f"Agent service error: {e.message}")
    return HTTPException(status_code=500, detail="Internal agent service error")


def handle_overlay_exception(e: Exception) -> HTTPException:
    """Convert overlay service exception to HTTP exception."""
    if isinstance(e, OverlayServiceException):
        return HTTPException(status_code=503, detail=f"Overlay service error: {e.message}")
    return HTTPException(status_code=500, detail="Internal overlay service error")
