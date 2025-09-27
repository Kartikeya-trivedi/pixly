"""
Overlay service for managing game overlay interactions.
Handles communication between backend and Electron frontend.
"""

from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime, timedelta

from src.services.agent_service import AgentService
from src.schemas.tip import TipSearchRequest

logger = logging.getLogger(__name__)


class OverlayService:
    """Service for overlay-specific operations and state management."""
    
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.update_interval = 5  # seconds
    
    async def start_overlay_session(self, session_id: str, game: str) -> bool:
        """
        Start a new overlay session for a game.
        
        Args:
            session_id: Unique session identifier
            game: Game name
        
        Returns:
            bool: Success status
        """
        try:
            self.active_sessions[session_id] = {
                "game": game,
                "started_at": datetime.now(),
                "last_update": datetime.now(),
                "context": "",
                "tips_shown": []
            }
            
            logger.info(f"Started overlay session {session_id} for game {game}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start overlay session: {e}")
            return False
    
    async def stop_overlay_session(self, session_id: str) -> bool:
        """
        Stop an overlay session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            bool: Success status
        """
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Stopped overlay session {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop overlay session: {e}")
            return False
    
    async def update_game_context(self, session_id: str, context: str) -> Optional[List[Dict[str, Any]]]:
        """
        Update game context and get relevant tips.
        
        Args:
            session_id: Session identifier
            context: Current game context/state
        
        Returns:
            List of relevant tips or None
        """
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            session["context"] = context
            session["last_update"] = datetime.now()
            
            # Get contextual tips
            request = TipSearchRequest(
                game=session["game"],
                query=context,
                limit=3
            )
            
            response = self.agent_service.process_game_query(request)
            
            # Filter out already shown tips
            new_tips = []
            for tip in response.tips:
                tip_id = str(tip.get("id", ""))
                if tip_id not in session["tips_shown"]:
                    new_tips.append(tip)
                    session["tips_shown"].append(tip_id)
            
            return new_tips
            
        except Exception as e:
            logger.error(f"Failed to update game context: {e}")
            return None
    
    async def get_periodic_tips(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get periodic tips for an active session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of tips or None
        """
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Check if enough time has passed since last update
            time_since_update = datetime.now() - session["last_update"]
            if time_since_update.total_seconds() < self.update_interval:
                return None
            
            # Get general tips for the game
            request = TipSearchRequest(
                game=session["game"],
                limit=2
            )
            
            response = self.agent_service.process_game_query(request)
            
            # Filter out already shown tips
            new_tips = []
            for tip in response.tips:
                tip_id = str(tip.get("id", ""))
                if tip_id not in session["tips_shown"]:
                    new_tips.append(tip)
                    session["tips_shown"].append(tip_id)
            
            return new_tips
            
        except Exception as e:
            logger.error(f"Failed to get periodic tips: {e}")
            return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an active session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session information or None
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id].copy()
            session["duration"] = (datetime.now() - session["started_at"]).total_seconds()
            return session
        return None
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self.active_sessions.keys())
    
    async def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """
        Clean up sessions that have been inactive for too long.
        
        Args:
            timeout_minutes: Minutes of inactivity before cleanup
        """
        try:
            current_time = datetime.now()
            timeout_delta = timedelta(minutes=timeout_minutes)
            
            inactive_sessions = []
            for session_id, session in self.active_sessions.items():
                if current_time - session["last_update"] > timeout_delta:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                await self.stop_overlay_session(session_id)
                logger.info(f"Cleaned up inactive session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
