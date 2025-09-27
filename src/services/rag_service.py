"""
RAG (Retrieval-Augmented Generation) service.
Handles vector database operations and LLM integration for generating contextual tips.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations using ChromaDB and Gemini."""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.llm = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize ChromaDB, embedding model, and LLM."""
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.VECTOR_DB_COLLECTION_NAME
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Initialize Gemini LLM
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.llm = genai.GenerativeModel('gemini-pro')
            else:
                logger.warning("GEMINI_API_KEY not set. LLM features will be limited.")
                
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents with 'content', 'metadata', and 'id' fields
        
        Returns:
            bool: Success status
        """
        try:
            if not documents:
                return False
            
            # Extract content and metadata
            contents = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            ids = [doc["id"] for doc in documents]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(contents).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def search_similar(self, query: str, game: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query: Search query
            game: Game name to filter by
            limit: Maximum number of results
        
        Returns:
            List of similar documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"game": game} if game else None
            )
            
            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    def generate_contextual_tip(self, query: str, game: str, context_docs: List[Dict[str, Any]]) -> Optional[str]:
        """
        Generate a contextual tip using LLM and retrieved context.
        
        Args:
            query: User query
            game: Game name
            context_docs: Retrieved context documents
        
        Returns:
            Generated tip or None if LLM is not available
        """
        if not self.llm:
            logger.warning("LLM not available. Cannot generate contextual tips.")
            return None
        
        try:
            # Prepare context
            context_text = "\n\n".join([doc["content"] for doc in context_docs])
            
            # Create prompt
            prompt = f"""
            You are a helpful game assistant for {game}. 
            Based on the following context and user query, provide a helpful tip or walkthrough.
            
            User Query: {query}
            
            Context:
            {context_text}
            
            Please provide a concise, helpful tip that directly addresses the user's query.
            Keep it under 200 words and make it actionable.
            """
            
            # Generate response
            response = self.llm.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Failed to generate contextual tip: {e}")
            return None
    
    def get_tips_with_rag(self, query: str, game: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get tips using RAG pipeline: retrieve relevant documents and generate contextual tips.
        
        Args:
            query: User query
            game: Game name
            limit: Maximum number of tips
        
        Returns:
            List of tips with content and metadata
        """
        try:
            # Step 1: Retrieve similar documents
            similar_docs = self.search_similar(query, game, limit)
            
            if not similar_docs:
                logger.info(f"No similar documents found for query: {query}")
                return []
            
            # Step 2: Generate contextual tips
            tips = []
            for doc in similar_docs:
                # Use the document content as base tip
                tip_content = doc["content"]
                
                # Optionally enhance with LLM if available
                if self.llm and len(similar_docs) > 1:
                    enhanced_tip = self.generate_contextual_tip(query, game, [doc])
                    if enhanced_tip:
                        tip_content = enhanced_tip
                
                tips.append({
                    "content": tip_content,
                    "metadata": doc["metadata"],
                    "relevance_score": 1.0 - doc.get("distance", 0.0)
                })
            
            return tips
            
        except Exception as e:
            logger.error(f"Failed to get tips with RAG: {e}")
            return []
