#!/usr/bin/env python3
"""
Sample ETL script for Game Overlay AI.
Ingests sample game data into the vector database.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.etl_service import ETLService
from src.services.rag_service import RAGService
from src.db.database import create_tables
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample game data for testing."""
    sample_data = {
        "minecraft": [
            {
                "title": "Getting Started with Minecraft",
                "content": "Start by gathering wood from trees. Use your fists to punch trees and collect wood blocks. Create a crafting table and make basic tools like a wooden pickaxe.",
                "category": "beginner",
                "difficulty": "easy",
                "source": "sample_data"
            },
            {
                "title": "Building Your First House",
                "content": "Find a flat area and build a simple 4x4 house with walls 3 blocks high. Use any block type for walls and place a door for entry. Add torches for lighting.",
                "category": "building",
                "difficulty": "easy",
                "source": "sample_data"
            },
            {
                "title": "Mining for Resources",
                "content": "Dig down to find coal, iron, and other ores. Coal is found at any depth, iron at Y=63 and below. Use a stone pickaxe or better to mine iron.",
                "category": "mining",
                "difficulty": "medium",
                "source": "sample_data"
            },
            {
                "title": "Redstone Contraptions",
                "content": "Redstone is Minecraft's electrical system. Use redstone dust, repeaters, and comparators to create automatic farms, doors, and complex machines.",
                "category": "advanced",
                "difficulty": "hard",
                "source": "sample_data"
            }
        ],
        "elden_ring": [
            {
                "title": "Character Creation Tips",
                "content": "Choose a class that matches your playstyle. Vagabond is good for beginners, Astrologer for magic users, and Samurai for balanced combat.",
                "category": "beginner",
                "difficulty": "easy",
                "source": "sample_data"
            },
            {
                "title": "Combat Basics",
                "content": "Learn to dodge, block, and parry. Stamina management is crucial. Don't get greedy with attacks - wait for openings.",
                "category": "combat",
                "difficulty": "medium",
                "source": "sample_data"
            },
            {
                "title": "Boss Strategies",
                "content": "Study boss attack patterns. Most bosses have 2-3 phases. Use spirit ashes for help, and don't be afraid to level up before challenging difficult bosses.",
                "category": "bosses",
                "difficulty": "hard",
                "source": "sample_data"
            }
        ],
        "cyberpunk_2077": [
            {
                "title": "Character Builds",
                "content": "Focus on one attribute tree initially. Netrunner for hacking, Solo for combat, or Techie for crafting. You can respec attributes later.",
                "category": "character",
                "difficulty": "medium",
                "source": "sample_data"
            },
            {
                "title": "Cyberware Upgrades",
                "content": "Visit ripperdocs to install cyberware. Start with basic implants like optical scanner and subdermal armor. Save eddies for expensive upgrades.",
                "category": "upgrades",
                "difficulty": "medium",
                "source": "sample_data"
            }
        ]
    }
    return sample_data


def run_etl_pipeline():
    """Run the ETL pipeline with sample data."""
    try:
        logger.info("Starting ETL pipeline...")
        
        # Initialize database
        logger.info("Creating database tables...")
        create_tables()
        
        # Initialize services
        etl_service = ETLService()
        rag_service = RAGService()
        
        # Get sample data
        sample_data = create_sample_data()
        
        # Process each game
        all_documents = []
        for game_name, tips in sample_data.items():
            logger.info(f"Processing {game_name}...")
            
            for i, tip in enumerate(tips):
                document = {
                    "id": f"{game_name}_{i}",
                    "content": f"{tip['title']}\n\n{tip['content']}",
                    "metadata": {
                        "game": game_name,
                        "title": tip["title"],
                        "category": tip["category"],
                        "difficulty": tip["difficulty"],
                        "source": tip["source"]
                    }
                }
                all_documents.append(document)
        
        # Load documents into vector database
        logger.info(f"Loading {len(all_documents)} documents into vector database...")
        success = etl_service.load_to_vector_db(all_documents)
        
        if success:
            logger.info("ETL pipeline completed successfully!")
            
            # Test retrieval
            logger.info("Testing retrieval...")
            test_queries = [
                ("minecraft", "How do I build a house?"),
                ("elden_ring", "What's the best starting class?"),
                ("cyberpunk_2077", "How do I upgrade my character?")
            ]
            
            for game, query in test_queries:
                results = rag_service.search_similar(query, game, limit=2)
                logger.info(f"Query: '{query}' for {game}")
                for result in results:
                    logger.info(f"  - {result['metadata'].get('title', 'No title')}")
                    logger.info(f"    Distance: {result.get('distance', 'N/A')}")
        else:
            logger.error("ETL pipeline failed!")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        return False


if __name__ == "__main__":
    success = run_etl_pipeline()
    sys.exit(0 if success else 1)
