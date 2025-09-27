"""
Pydantic schemas for tip-related API requests and responses.
Defines data validation and serialization models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TipBase(BaseModel):
    """Base tip schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, max_length=20)


class TipCreate(TipBase):
    """Schema for creating a new tip."""
    game_id: int = Field(..., gt=0)


class TipUpdate(BaseModel):
    """Schema for updating an existing tip."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, max_length=20)
    is_verified: Optional[bool] = None


class TipResponse(TipBase):
    """Schema for tip API responses."""
    id: int
    game_id: int
    is_verified: bool
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TipSearchRequest(BaseModel):
    """Schema for tip search requests."""
    game: str = Field(..., min_length=1, max_length=100)
    query: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, max_length=20)
    limit: int = Field(5, ge=1, le=20)


class TipSearchResponse(BaseModel):
    """Schema for tip search responses."""
    tips: List[TipResponse]
    total_found: int
    game: str
    query: Optional[str] = None
