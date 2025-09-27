"""
Repository layer for tip data access.
Handles database operations for tips and games.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from src.models.game import Tip, Game
from src.schemas.tip import TipCreate, TipUpdate


class TipRepository:
    """Repository for tip-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tip(self, tip_data: TipCreate) -> Tip:
        """Create a new tip."""
        tip = Tip(**tip_data.dict())
        self.db.add(tip)
        self.db.commit()
        self.db.refresh(tip)
        return tip
    
    def get_tip_by_id(self, tip_id: int) -> Optional[Tip]:
        """Get a tip by ID."""
        return self.db.query(Tip).filter(Tip.id == tip_id).first()
    
    def get_tips_by_game(self, game_name: str, limit: int = 10) -> List[Tip]:
        """Get tips for a specific game."""
        return (
            self.db.query(Tip)
            .join(Game)
            .filter(and_(Game.name.ilike(f"%{game_name}%"), Game.is_active == True))
            .limit(limit)
            .all()
        )
    
    def search_tips(
        self, 
        game_name: str, 
        query: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[Tip]:
        """Search tips with filters."""
        query_obj = (
            self.db.query(Tip)
            .join(Game)
            .filter(and_(Game.name.ilike(f"%{game_name}%"), Game.is_active == True))
        )
        
        if query:
            query_obj = query_obj.filter(
                or_(
                    Tip.title.ilike(f"%{query}%"),
                    Tip.content.ilike(f"%{query}%")
                )
            )
        
        if category:
            query_obj = query_obj.filter(Tip.category == category)
        
        if difficulty:
            query_obj = query_obj.filter(Tip.difficulty == difficulty)
        
        return query_obj.limit(limit).all()
    
    def update_tip(self, tip_id: int, tip_data: TipUpdate) -> Optional[Tip]:
        """Update an existing tip."""
        tip = self.get_tip_by_id(tip_id)
        if not tip:
            return None
        
        update_data = tip_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tip, field, value)
        
        self.db.commit()
        self.db.refresh(tip)
        return tip
    
    def delete_tip(self, tip_id: int) -> bool:
        """Delete a tip."""
        tip = self.get_tip_by_id(tip_id)
        if not tip:
            return False
        
        self.db.delete(tip)
        self.db.commit()
        return True
    
    def get_or_create_game(self, game_name: str) -> Game:
        """Get existing game or create new one."""
        game = self.db.query(Game).filter(Game.name == game_name).first()
        if not game:
            game = Game(name=game_name, description=f"Game: {game_name}")
            self.db.add(game)
            self.db.commit()
            self.db.refresh(game)
        return game
