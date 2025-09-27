"""
Test suite for the tips API endpoints.
Tests the /tips endpoint functionality with various scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.database import get_db, Base
from src.models.game import Game, Tip


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client with overridden dependencies."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_game():
    """Create a sample game for testing."""
    return {
        "name": "test_game",
        "description": "A test game for unit testing",
        "genre": "adventure",
        "platform": "PC"
    }


@pytest.fixture
def sample_tips():
    """Create sample tips for testing."""
    return [
        {
            "title": "Test Tip 1",
            "content": "This is a test tip for beginners",
            "category": "beginner",
            "difficulty": "easy"
        },
        {
            "title": "Test Tip 2", 
            "content": "This is an advanced test tip",
            "category": "advanced",
            "difficulty": "hard"
        }
    ]


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_get_tips_basic(client, sample_game, sample_tips):
    """Test basic tips retrieval."""
    # Create test data
    db = TestingSessionLocal()
    
    # Create game
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    # Create tips
    for tip_data in sample_tips:
        tip = Tip(
            game_id=game.id,
            **tip_data
        )
        db.add(tip)
    db.commit()
    db.close()
    
    # Test API call
    response = client.get("/api/v1/tips?game=test_game")
    assert response.status_code == 200
    
    data = response.json()
    assert "tips" in data
    assert "total_found" in data
    assert data["game"] == "test_game"
    assert len(data["tips"]) == 2


def test_get_tips_with_query(client, sample_game, sample_tips):
    """Test tips retrieval with search query."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    for tip_data in sample_tips:
        tip = Tip(game_id=game.id, **tip_data)
        db.add(tip)
    db.commit()
    db.close()
    
    # Test with query
    response = client.get("/api/v1/tips?game=test_game&query=beginner")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tips"]) >= 1
    # Should find the beginner tip
    assert any("beginner" in tip["content"].lower() or "beginner" in tip["title"].lower() 
              for tip in data["tips"])


def test_get_tips_with_filters(client, sample_game, sample_tips):
    """Test tips retrieval with category and difficulty filters."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    for tip_data in sample_tips:
        tip = Tip(game_id=game.id, **tip_data)
        db.add(tip)
    db.commit()
    db.close()
    
    # Test with category filter
    response = client.get("/api/v1/tips?game=test_game&category=beginner")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tips"]) >= 1
    assert all(tip["category"] == "beginner" for tip in data["tips"])
    
    # Test with difficulty filter
    response = client.get("/api/v1/tips?game=test_game&difficulty=easy")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tips"]) >= 1
    assert all(tip["difficulty"] == "easy" for tip in data["tips"])


def test_get_tips_limit(client, sample_game, sample_tips):
    """Test tips retrieval with limit parameter."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    for tip_data in sample_tips:
        tip = Tip(game_id=game.id, **tip_data)
        db.add(tip)
    db.commit()
    db.close()
    
    # Test with limit
    response = client.get("/api/v1/tips?game=test_game&limit=1")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["tips"]) == 1


def test_get_tips_nonexistent_game(client):
    """Test tips retrieval for non-existent game."""
    response = client.get("/api/v1/tips?game=nonexistent_game")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_found"] == 0
    assert len(data["tips"]) == 0


def test_get_tips_missing_game_parameter(client):
    """Test tips retrieval without required game parameter."""
    response = client.get("/api/v1/tips")
    assert response.status_code == 422  # Validation error


def test_get_tips_invalid_limit(client):
    """Test tips retrieval with invalid limit parameter."""
    response = client.get("/api/v1/tips?game=test_game&limit=100")
    assert response.status_code == 422  # Validation error (limit too high)


def test_create_tip(client, sample_game):
    """Test creating a new tip."""
    # Create game first
    db = TestingSessionLocal()
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    db.close()
    
    # Create tip
    tip_data = {
        "game_id": game.id,
        "title": "New Test Tip",
        "content": "This is a newly created test tip",
        "category": "test",
        "difficulty": "medium"
    }
    
    response = client.post("/api/v1/tips", json=tip_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == tip_data["title"]
    assert data["content"] == tip_data["content"]
    assert data["game_id"] == game.id


def test_get_tip_by_id(client, sample_game, sample_tips):
    """Test retrieving a specific tip by ID."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    tip = Tip(game_id=game.id, **sample_tips[0])
    db.add(tip)
    db.commit()
    db.refresh(tip)
    db.close()
    
    # Test API call
    response = client.get(f"/api/v1/tips/{tip.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == tip.id
    assert data["title"] == sample_tips[0]["title"]


def test_get_tip_nonexistent_id(client):
    """Test retrieving a tip with non-existent ID."""
    response = client.get("/api/v1/tips/99999")
    assert response.status_code == 404


def test_update_tip(client, sample_game, sample_tips):
    """Test updating an existing tip."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    tip = Tip(game_id=game.id, **sample_tips[0])
    db.add(tip)
    db.commit()
    db.refresh(tip)
    db.close()
    
    # Update tip
    update_data = {
        "title": "Updated Test Tip",
        "content": "This tip has been updated"
    }
    
    response = client.put(f"/api/v1/tips/{tip.id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]


def test_delete_tip(client, sample_game, sample_tips):
    """Test deleting a tip."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    tip = Tip(game_id=game.id, **sample_tips[0])
    db.add(tip)
    db.commit()
    db.refresh(tip)
    db.close()
    
    # Delete tip
    response = client.delete(f"/api/v1/tips/{tip.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Tip deleted successfully"
    
    # Verify tip is deleted
    response = client.get(f"/api/v1/tips/{tip.id}")
    assert response.status_code == 404


def test_get_game_tips(client, sample_game, sample_tips):
    """Test getting all tips for a specific game."""
    # Create test data
    db = TestingSessionLocal()
    
    game = Game(**sample_game)
    db.add(game)
    db.commit()
    db.refresh(game)
    
    for tip_data in sample_tips:
        tip = Tip(game_id=game.id, **tip_data)
        db.add(tip)
    db.commit()
    db.close()
    
    # Test API call
    response = client.get(f"/api/v1/games/{sample_game['name']}/tips")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(tip["game_id"] == game.id for tip in data)
