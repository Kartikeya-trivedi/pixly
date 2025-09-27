"""
Configuration management using Pydantic settings.
Handles environment variables and application configuration.
"""

from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./game_overlay.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # AI/LLM settings
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # RAG settings
    VECTOR_DB_COLLECTION_NAME: str = "game_guides"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Overlay settings
    OVERLAY_UPDATE_INTERVAL: int = 5  # seconds
    MAX_TIPS_PER_REQUEST: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
