"""
Test suite for the RAG service.
Tests vector database operations and LLM integration.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.services.rag_service import RAGService
from src.config import settings


@pytest.fixture
def temp_chroma_dir():
    """Create temporary directory for ChromaDB testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        {
            "id": "doc1",
            "content": "Minecraft is a sandbox game where you can build anything you can imagine. Start by gathering wood and building a shelter.",
            "metadata": {
                "game": "minecraft",
                "title": "Minecraft Basics",
                "category": "beginner"
            }
        },
        {
            "id": "doc2", 
            "content": "In Elden Ring, combat is about timing and patience. Learn enemy attack patterns and don't get greedy with your attacks.",
            "metadata": {
                "game": "elden_ring",
                "title": "Combat Guide",
                "category": "combat"
            }
        },
        {
            "id": "doc3",
            "content": "Redstone in Minecraft allows you to create complex machines and contraptions. Start with simple circuits and build up complexity.",
            "metadata": {
                "game": "minecraft",
                "title": "Redstone Engineering",
                "category": "advanced"
            }
        }
    ]


@pytest.fixture
def rag_service(temp_chroma_dir):
    """Create RAG service instance for testing."""
    # Override settings for testing
    original_chroma_dir = settings.CHROMA_PERSIST_DIRECTORY
    settings.CHROMA_PERSIST_DIRECTORY = temp_chroma_dir
    
    try:
        service = RAGService()
        yield service
    finally:
        settings.CHROMA_PERSIST_DIRECTORY = original_chroma_dir


def test_rag_service_initialization(rag_service):
    """Test RAG service initialization."""
    assert rag_service is not None
    assert rag_service.chroma_client is not None
    assert rag_service.collection is not None
    assert rag_service.embedding_model is not None


def test_add_documents(rag_service, sample_documents):
    """Test adding documents to vector database."""
    success = rag_service.add_documents(sample_documents)
    assert success is True


def test_search_similar_documents(rag_service, sample_documents):
    """Test searching for similar documents."""
    # Add documents first
    rag_service.add_documents(sample_documents)
    
    # Search for similar documents
    results = rag_service.search_similar("How do I build in Minecraft?", "minecraft", limit=2)
    
    assert len(results) > 0
    assert all("minecraft" in result["metadata"].get("game", "") for result in results)


def test_search_similar_no_results(rag_service):
    """Test searching with no matching documents."""
    results = rag_service.search_similar("Non-existent game query", "nonexistent_game", limit=5)
    assert len(results) == 0


def test_search_similar_empty_collection(rag_service):
    """Test searching in empty collection."""
    results = rag_service.search_similar("Any query", "any_game", limit=5)
    assert len(results) == 0


def test_get_tips_with_rag(rag_service, sample_documents):
    """Test getting tips using RAG pipeline."""
    # Add documents first
    rag_service.add_documents(sample_documents)
    
    # Get tips using RAG
    tips = rag_service.get_tips_with_rag("How to build in Minecraft?", "minecraft", limit=2)
    
    assert len(tips) > 0
    assert all("content" in tip for tip in tips)
    assert all("metadata" in tip for tip in tips)
    assert all("relevance_score" in tip for tip in tips)


def test_get_tips_with_rag_no_results(rag_service):
    """Test RAG pipeline with no matching documents."""
    tips = rag_service.get_tips_with_rag("Non-existent query", "nonexistent_game", limit=5)
    assert len(tips) == 0


def test_generate_contextual_tip_without_llm(rag_service, sample_documents):
    """Test contextual tip generation without LLM (should return None)."""
    # Add documents first
    rag_service.add_documents(sample_documents)
    
    # Search for similar documents
    similar_docs = rag_service.search_similar("Minecraft building", "minecraft", limit=2)
    
    # Try to generate contextual tip (without LLM configured)
    tip = rag_service.generate_contextual_tip("How to build?", "minecraft", similar_docs)
    
    # Should return None since LLM is not configured in tests
    assert tip is None


def test_add_documents_empty_list(rag_service):
    """Test adding empty document list."""
    success = rag_service.add_documents([])
    assert success is False


def test_add_documents_invalid_format(rag_service):
    """Test adding documents with invalid format."""
    invalid_docs = [
        {"id": "doc1"},  # Missing content
        {"content": "Some content"},  # Missing id
    ]
    
    success = rag_service.add_documents(invalid_docs)
    assert success is False


def test_search_with_different_games(rag_service, sample_documents):
    """Test searching across different games."""
    # Add documents
    rag_service.add_documents(sample_documents)
    
    # Search for Minecraft-specific content
    minecraft_results = rag_service.search_similar("building", "minecraft", limit=5)
    assert len(minecraft_results) > 0
    assert all("minecraft" in result["metadata"].get("game", "") for result in minecraft_results)
    
    # Search for Elden Ring content
    elden_ring_results = rag_service.search_similar("combat", "elden_ring", limit=5)
    assert len(elden_ring_results) > 0
    assert all("elden_ring" in result["metadata"].get("game", "") for result in elden_ring_results)


def test_relevance_scoring(rag_service, sample_documents):
    """Test that relevance scoring works correctly."""
    # Add documents
    rag_service.add_documents(sample_documents)
    
    # Search for very specific query
    results = rag_service.search_similar("Minecraft building basics", "minecraft", limit=3)
    
    if len(results) > 1:
        # Results should be ordered by relevance (lower distance = higher relevance)
        distances = [result.get("distance", 1.0) for result in results]
        assert distances == sorted(distances)


def test_metadata_preservation(rag_service, sample_documents):
    """Test that metadata is preserved in search results."""
    # Add documents
    rag_service.add_documents(sample_documents)
    
    # Search for documents
    results = rag_service.search_similar("Minecraft", "minecraft", limit=2)
    
    for result in results:
        assert "metadata" in result
        assert "game" in result["metadata"]
        assert result["metadata"]["game"] == "minecraft"


def test_limit_parameter(rag_service, sample_documents):
    """Test that limit parameter works correctly."""
    # Add documents
    rag_service.add_documents(sample_documents)
    
    # Search with different limits
    results_1 = rag_service.search_similar("game", "minecraft", limit=1)
    results_2 = rag_service.search_similar("game", "minecraft", limit=3)
    
    assert len(results_1) <= 1
    assert len(results_2) <= 3
