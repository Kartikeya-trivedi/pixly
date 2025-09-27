"""
Agent service for AI-powered game assistance.
Handles agent orchestration and decision making for game overlay interactions.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.services.rag_service import RAGService
from src.repositories.tip_repository import TipRepository
from src.schemas.tip import TipSearchRequest, TipSearchResponse

logger = logging.getLogger(__name__)


class AgentService:
    """Service for AI agent operations and game assistance."""
    
    def __init__(self, rag_service: RAGService, tip_repository: TipRepository):
        self.rag_service = rag_service
        self.tip_repository = tip_repository
    
    def process_game_query(self, request: TipSearchRequest) -> TipSearchResponse:
        """
        Process a game query using AI agent logic.
        
        Args:
            request: Search request with game and query parameters
        
        Returns:
            Structured response with tips and metadata
        """
        try:
            # Step 1: Get tips from database
            db_tips = self.tip_repository.search_tips(
                game_name=request.game,
                query=request.query,
                category=request.category,
                difficulty=request.difficulty,
                limit=request.limit
            )
            
            # Step 2: Get RAG-enhanced tips
            rag_tips = []
            if request.query:
                rag_results = self.rag_service.get_tips_with_rag(
                    query=request.query,
                    game=request.game,
                    limit=request.limit
                )
                rag_tips = rag_results
            
            # Step 3: Combine and rank results
            combined_tips = self._combine_and_rank_tips(db_tips, rag_tips, request.limit)
            
            # Step 4: Format response
            response = TipSearchResponse(
                tips=combined_tips,
                total_found=len(combined_tips),
                game=request.game,
                query=request.query
            )
            
            logger.info(f"Processed query for {request.game}: {len(combined_tips)} tips found")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process game query: {e}")
            return TipSearchResponse(
                tips=[],
                total_found=0,
                game=request.game,
                query=request.query
            )
    
    def _combine_and_rank_tips(
        self, 
        db_tips: List[Any], 
        rag_tips: List[Dict[str, Any]], 
        limit: int
    ) -> List[Any]:
        """
        Combine database tips with RAG tips and rank by relevance.
        
        Args:
            db_tips: Tips from database
            rag_tips: Tips from RAG service
            limit: Maximum number of tips to return
        
        Returns:
            Combined and ranked list of tips
        """
        # Convert database tips to response format
        db_tip_responses = []
        for tip in db_tips:
            db_tip_responses.append({
                "id": tip.id,
                "title": tip.title,
                "content": tip.content,
                "category": tip.category,
                "difficulty": tip.difficulty,
                "game_id": tip.game_id,
                "is_verified": tip.is_verified,
                "source_url": tip.source_url,
                "created_at": tip.created_at,
                "updated_at": tip.updated_at,
                "relevance_score": 0.8  # Default score for DB tips
            })
        
        # Convert RAG tips to response format
        rag_tip_responses = []
        for i, rag_tip in enumerate(rag_tips):
            rag_tip_responses.append({
                "id": f"rag_{i}",
                "title": f"AI-Generated Tip",
                "content": rag_tip["content"],
                "category": rag_tip.get("metadata", {}).get("category", "ai_generated"),
                "difficulty": rag_tip.get("metadata", {}).get("difficulty", "medium"),
                "game_id": None,
                "is_verified": False,
                "source_url": None,
                "created_at": datetime.now(),
                "updated_at": None,
                "relevance_score": rag_tip.get("relevance_score", 0.5)
            })
        
        # Combine and sort by relevance score
        all_tips = db_tip_responses + rag_tip_responses
        all_tips.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return all_tips[:limit]
    
    def get_contextual_help(self, game: str, current_context: str) -> Optional[str]:
        """
        Get contextual help based on current game state.
        
        Args:
            game: Game name
            current_context: Current game context/state
        
        Returns:
            Contextual help text or None
        """
        try:
            # Use RAG to find relevant context
            rag_results = self.rag_service.get_tips_with_rag(
                query=current_context,
                game=game,
                limit=1
            )
            
            if rag_results:
                return rag_results[0]["content"]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get contextual help: {e}")
            return None
