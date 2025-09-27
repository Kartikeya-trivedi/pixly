"""
ETL (Extract, Transform, Load) service.
Handles data ingestion from various sources into the vector database.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
import json
import time
from urllib.parse import urljoin, urlparse

from src.services.rag_service import RAGService
from src.config import settings

logger = logging.getLogger(__name__)


class ETLService:
    """Service for extracting, transforming, and loading game data."""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Game Overlay AI ETL Bot 1.0'
        })
    
    def extract_from_url(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Extract content from a web URL.
        
        Args:
            url: URL to extract from
            max_pages: Maximum number of pages to crawl
        
        Returns:
            List of extracted documents
        """
        try:
            documents = []
            visited_urls = set()
            urls_to_visit = [url]
            
            while urls_to_visit and len(documents) < max_pages:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                
                visited_urls.add(current_url)
                
                try:
                    response = self.session.get(current_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract main content
                    content = self._extract_text_content(soup)
                    if content:
                        documents.append({
                            "id": f"web_{len(documents)}",
                            "content": content,
                            "metadata": {
                                "source": "web",
                                "url": current_url,
                                "title": soup.title.string if soup.title else "",
                                "extracted_at": time.time()
                            }
                        })
                    
                    # Find additional links to crawl
                    if len(documents) < max_pages:
                        new_urls = self._extract_links(soup, current_url)
                        urls_to_visit.extend(new_urls[:5])  # Limit new URLs per page
                    
                    # Be respectful with requests
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract from {current_url}: {e}")
                    continue
            
            logger.info(f"Extracted {len(documents)} documents from {url}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to extract from URL {url}: {e}")
            return []
    
    def extract_from_json(self, json_data: List[Dict[str, Any]], game_name: str) -> List[Dict[str, Any]]:
        """
        Extract content from JSON data.
        
        Args:
            json_data: List of JSON objects with game data
            game_name: Name of the game
        
        Returns:
            List of extracted documents
        """
        documents = []
        
        for i, item in enumerate(json_data):
            content = ""
            metadata = {"source": "json", "game": game_name}
            
            # Extract text content from various fields
            for field in ["content", "text", "description", "tip", "guide"]:
                if field in item and item[field]:
                    content += f"{item[field]}\n"
            
            # Add other metadata
            for field in ["title", "category", "difficulty", "author"]:
                if field in item:
                    metadata[field] = item[field]
            
            if content.strip():
                documents.append({
                    "id": f"json_{game_name}_{i}",
                    "content": content.strip(),
                    "metadata": metadata
                })
        
        logger.info(f"Extracted {len(documents)} documents from JSON for {game_name}")
        return documents
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML soup."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
        
        if main_content:
            return main_content.get_text(separator=" ", strip=True)
        else:
            return soup.get_text(separator=" ", strip=True)
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract relevant links from HTML soup."""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)
            
            # Only include links from the same domain
            if urlparse(full_url).netloc == base_domain:
                links.append(full_url)
        
        return links
    
    def load_to_vector_db(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Load documents into the vector database.
        
        Args:
            documents: List of documents to load
        
        Returns:
            bool: Success status
        """
        return self.rag_service.add_documents(documents)
    
    def etl_pipeline(self, sources: List[Dict[str, Any]]) -> bool:
        """
        Run complete ETL pipeline for multiple sources.
        
        Args:
            sources: List of source configurations
        
        Returns:
            bool: Success status
        """
        try:
            all_documents = []
            
            for source in sources:
                source_type = source.get("type")
                source_config = source.get("config", {})
                
                if source_type == "url":
                    documents = self.extract_from_url(
                        source_config.get("url"),
                        source_config.get("max_pages", 10)
                    )
                elif source_type == "json":
                    documents = self.extract_from_json(
                        source_config.get("data", []),
                        source_config.get("game_name", "unknown")
                    )
                else:
                    logger.warning(f"Unknown source type: {source_type}")
                    continue
                
                all_documents.extend(documents)
            
            # Load all documents to vector database
            if all_documents:
                success = self.load_to_vector_db(all_documents)
                logger.info(f"ETL pipeline completed. Loaded {len(all_documents)} documents.")
                return success
            else:
                logger.warning("No documents extracted from sources")
                return False
                
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return False
