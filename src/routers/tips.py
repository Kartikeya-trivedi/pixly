"""
Tips router for game tips and walkthroughs.
Handles tip search, retrieval, and management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.db.database import get_db
from src.repositories.tip_repository import TipRepository
from src.services.rag_service import RAGService
from src.services.agent_service import AgentService
from src.services.overlay_service import OverlayService
from src.schemas.tip import (
    TipSearchRequest, 
    TipSearchResponse, 
    TipCreate, 
    TipUpdate, 
    TipResponse
)

router = APIRouter(tags=["tips"])

# Initialize services (in production, use dependency injection)
_rag_service = None
_agent_service = None
_overlay_service = None

def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

def get_agent_service() -> AgentService:
    """Get agent service instance."""
    global _agent_service
    if _agent_service is None:
        rag_service = get_rag_service()
        tip_repo = TipRepository(db=next(get_db()))
        _agent_service = AgentService(rag_service, tip_repo)
    return _agent_service

def get_overlay_service() -> OverlayService:
    """Get overlay service instance."""
    global _overlay_service
    if _overlay_service is None:
        agent_service = get_agent_service()
        _overlay_service = OverlayService(agent_service)
    return _overlay_service


@router.get("/tips", response_model=TipSearchResponse)
async def get_tips(
    game: str = Query(..., description="Game name to search tips for"),
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Tip category filter"),
    difficulty: Optional[str] = Query(None, description="Difficulty level filter"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of tips to return"),
    db: Session = Depends(get_db)
) -> TipSearchResponse:
    """
    Get tips for a specific game with optional filters.
    This is the main endpoint for the game overlay.
    """
    try:
        # Create search request
        request = TipSearchRequest(
            game=game,
            query=query,
            category=category,
            difficulty=difficulty,
            limit=limit
        )
        
        # Process query using agent service
        agent_service = get_agent_service()
        response = agent_service.process_game_query(request)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tips: {str(e)}")


@router.post("/tips", response_model=TipResponse)
async def create_tip(
    tip_data: TipCreate,
    db: Session = Depends(get_db)
) -> TipResponse:
    """Create a new tip."""
    try:
        tip_repo = TipRepository(db)
        tip = tip_repo.create_tip(tip_data)
        return TipResponse.from_orm(tip)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create tip: {str(e)}")


@router.get("/tips/{tip_id}", response_model=TipResponse)
async def get_tip(
    tip_id: int,
    db: Session = Depends(get_db)
) -> TipResponse:
    """Get a specific tip by ID."""
    try:
        tip_repo = TipRepository(db)
        tip = tip_repo.get_tip_by_id(tip_id)
        
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        return TipResponse.from_orm(tip)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tip: {str(e)}")


@router.put("/tips/{tip_id}", response_model=TipResponse)
async def update_tip(
    tip_id: int,
    tip_data: TipUpdate,
    db: Session = Depends(get_db)
) -> TipResponse:
    """Update an existing tip."""
    try:
        tip_repo = TipRepository(db)
        tip = tip_repo.update_tip(tip_id, tip_data)
        
        if not tip:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        return TipResponse.from_orm(tip)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tip: {str(e)}")


@router.delete("/tips/{tip_id}")
async def delete_tip(
    tip_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a tip."""
    try:
        tip_repo = TipRepository(db)
        success = tip_repo.delete_tip(tip_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Tip not found")
        
        return {"message": "Tip deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tip: {str(e)}")


@router.get("/games/{game_name}/tips", response_model=List[TipResponse])
async def get_game_tips(
    game_name: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> List[TipResponse]:
    """Get all tips for a specific game."""
    try:
        tip_repo = TipRepository(db)
        tips = tip_repo.get_tips_by_game(game_name, limit)
        
        return [TipResponse.from_orm(tip) for tip in tips]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get game tips: {str(e)}")
