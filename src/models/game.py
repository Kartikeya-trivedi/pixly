"""
Game-related database models.
Defines SQLAlchemy models for games, tips, and user interactions.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.database import Base


class Game(Base):
    """Game model for storing game information."""
    
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    genre = Column(String(50))
    platform = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tips = relationship("Tip", back_populates="game")


class Tip(Base):
    """Tip model for storing game tips and walkthroughs."""
    
    __tablename__ = "tips"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # e.g., "beginner", "advanced", "walkthrough"
    difficulty = Column(String(20))  # e.g., "easy", "medium", "hard"
    is_verified = Column(Boolean, default=False)
    source_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="tips")


class UserInteraction(Base):
    """User interaction model for tracking tip usage and feedback."""
    
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tip_id = Column(Integer, ForeignKey("tips.id"), nullable=False)
    user_id = Column(String(100))  # Anonymous user ID
    interaction_type = Column(String(20))  # "view", "like", "dislike", "helpful"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tip = relationship("Tip")
