"""
Game Overlay AI - FastAPI Backend
Main application entry point with all routers and middleware configured.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.config import settings
from src.routers import tips, health
from src.middlewares import logging_middleware


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Game Overlay AI",
        description="AI-powered game overlay with walkthroughs and tips",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware for Electron frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom logging middleware
    app.middleware("http")(logging_middleware)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(tips.router, prefix="/api/v1")
    
    # Serve static files for Electron frontend
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
