#!/usr/bin/env python3
"""
Minecraft-specific ETL script.
Ingests Minecraft wiki and guide data into the vector database.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_minecraft_data():
    """Create comprehensive Minecraft game data."""
    minecraft_data = [
        {
            "title": "Minecraft Basics - First Steps",
            "content": """
            Welcome to Minecraft! Here's how to get started:
            
            1. **Gather Wood**: Punch trees to collect wood blocks
            2. **Craft Basic Tools**: Create a crafting table and wooden tools
            3. **Build Shelter**: Create a simple house before nightfall
            4. **Find Food**: Kill animals or grow crops for food
            5. **Explore**: Once established, explore caves and biomes
            
            Remember: The first night is the most dangerous!
            """,
            "category": "beginner",
            "difficulty": "easy"
        },
        {
            "title": "Mining Guide - Finding Ores",
            "content": """
            Mining is essential for progression in Minecraft:
            
            **Coal**: Found at any depth, used for torches and fuel
            **Iron**: Found at Y=63 and below, needed for tools and armor
            **Gold**: Found at Y=32 and below, used for powered rails and clocks
            **Diamond**: Found at Y=16 and below, best tools and armor
            **Redstone**: Found at Y=16 and below, used for redstone circuits
            **Lapis Lazuli**: Found at Y=32 and below, used for enchanting
            
            **Mining Tips**:
            - Always bring torches and food
            - Don't dig straight down
            - Use the F3 screen to check your Y coordinate
            """,
            "category": "mining",
            "difficulty": "medium"
        },
        {
            "title": "Building Techniques",
            "content": """
            Master these building techniques for better structures:
            
            **Foundation**: Always start with a solid foundation
            **Walls**: Use consistent materials and patterns
            **Roofing**: Add depth with overhangs and different materials
            **Lighting**: Place torches or glowstone for safety
            **Interior**: Add furniture, storage, and decorations
            
            **Advanced Techniques**:
            - Use stairs and slabs for detail
            - Create depth with different block types
            - Add windows and balconies
            - Use landscaping around your builds
            """,
            "category": "building",
            "difficulty": "medium"
        },
        {
            "title": "Redstone Engineering",
            "content": """
            Redstone is Minecraft's electrical system:
            
            **Basic Components**:
            - Redstone dust: carries power
            - Redstone torches: power sources
            - Repeaters: extend and delay signals
            - Comparators: detect and compare signals
            
            **Common Contraptions**:
            - Automatic doors
            - Hidden entrances
            - Item sorters
            - Automatic farms
            - Piston doors
            
            **Tips**:
            - Start simple and build complexity
            - Use redstone torches for inversion
            - Learn about signal strength
            - Practice with creative mode
            """,
            "category": "redstone",
            "difficulty": "hard"
        },
        {
            "title": "Combat and Enchanting",
            "content": """
            Master combat and enchanting for survival:
            
            **Combat Basics**:
            - Use shields to block attacks
            - Learn attack timing and combos
            - Keep food handy for healing
            - Use different weapons for different situations
            
            **Enchanting**:
            - Build an enchanting table with bookshelves
            - Use experience levels and lapis lazuli
            - Combine enchanted items in anvils
            - Look for specific enchantments
            
            **Useful Enchantments**:
            - Protection: reduces all damage
            - Sharpness: increases melee damage
            - Efficiency: faster mining
            - Fortune: more drops from ores
            - Unbreaking: items last longer
            """,
            "category": "combat",
            "difficulty": "medium"
        },
        {
            "title": "Nether and End Dimensions",
            "content": """
            Explore dangerous dimensions for rare resources:
            
            **The Nether**:
            - Build a portal with obsidian (4x5 frame)
            - Bring fire resistance potions
            - Find fortresses for blaze rods
            - Mine quartz and glowstone
            - Watch out for ghasts and piglins
            
            **The End**:
            - Find strongholds using eyes of ender
            - Defeat the ender dragon
            - Collect ender pearls and dragon egg
            - Explore end cities for elytra wings
            - Use ender chests for storage
            
            **Preparation**:
            - Bring plenty of food and armor
            - Use ender pearls for teleportation
            - Build bridges in the End
            - Collect shulker boxes for storage
            """,
            "category": "advanced",
            "difficulty": "hard"
        }
    ]
    
    return minecraft_data


def run_minecraft_etl():
    """Run ETL pipeline specifically for Minecraft data."""
    try:
        logger.info("Starting Minecraft ETL pipeline...")
        
        # Initialize database
        create_tables()
        
        # Initialize services
        etl_service = ETLService()
        
        # Get Minecraft data
        minecraft_data = create_minecraft_data()
        
        # Convert to documents
        documents = []
        for i, tip in enumerate(minecraft_data):
            document = {
                "id": f"minecraft_{i}",
                "content": tip["content"],
                "metadata": {
                    "game": "minecraft",
                    "title": tip["title"],
                    "category": tip["category"],
                    "difficulty": tip["difficulty"],
                    "source": "minecraft_guide"
                }
            }
            documents.append(document)
        
        # Load into vector database
        logger.info(f"Loading {len(documents)} Minecraft documents...")
        success = etl_service.load_to_vector_db(documents)
        
        if success:
            logger.info("Minecraft ETL completed successfully!")
            
            # Test some queries
            rag_service = RAGService()
            test_queries = [
                "How do I find diamonds?",
                "What's the best way to build a house?",
                "How does redstone work?",
                "What should I do in the Nether?"
            ]
            
            for query in test_queries:
                results = rag_service.search_similar(query, "minecraft", limit=2)
                logger.info(f"Query: '{query}'")
                for result in results:
                    logger.info(f"  - {result['metadata'].get('title', 'No title')}")
        else:
            logger.error("Minecraft ETL failed!")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Minecraft ETL failed: {e}")
        return False


if __name__ == "__main__":
    success = run_minecraft_etl()
    sys.exit(0 if success else 1)
