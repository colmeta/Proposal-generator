"""
Knowledge Base Service
ChromaDB-based vector database for storing and retrieving funder knowledge with semantic search
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Knowledge Base Service using ChromaDB for vector storage and semantic search
    
    Features:
    - Local ChromaDB instance (no external service)
    - Semantic search using sentence transformers
    - Store structured funder data
    - Query by similarity
    - Update and maintain knowledge
    """
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "funder_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Knowledge Base
        
        Args:
            persist_directory: Directory to persist ChromaDB data (default: ./data/knowledge_base)
            collection_name: Name of the ChromaDB collection
            embedding_model: Sentence transformer model name for embeddings
        """
        # Set up persistence directory
        if persist_directory is None:
            persist_directory = os.path.join(
                os.getcwd(), "data", "knowledge_base"
            )
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
        
        # Initialize ChromaDB client (local, persistent)
        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info(f"ChromaDB client initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
        
        # Create embedding function wrapper for ChromaDB
        def embedding_function(texts):
            """Embedding function for ChromaDB using sentence-transformers"""
            try:
                embeddings = self.embedding_model.encode(
                    texts,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise
        
        # Store embedding function for reuse
        self._embedding_function = embedding_function
        
        # Get or create collection with custom embedding function
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self._embedding_function,
                metadata={"description": "Funder knowledge and research data"}
            )
            logger.info(f"Collection '{collection_name}' ready")
        except Exception as e:
            logger.error(f"Failed to get/create collection: {e}")
            raise
    
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the knowledge base
        
        Args:
            content: Text content of the document
            metadata: Optional metadata dictionary
            document_id: Optional document ID (auto-generated if not provided)
        
        Returns:
            Document ID
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        # Generate document ID if not provided
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        # Prepare metadata
        doc_metadata = metadata.copy() if metadata else {}
        doc_metadata["content_length"] = len(content)
        
        try:
            # ChromaDB will use its own embedding function, but we can also provide embeddings
            # For now, let ChromaDB handle embeddings using the default function
            # We'll use the collection's add method
            self.collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[document_id]
            )
            
            logger.debug(f"Document added: {document_id}")
            return document_id
        
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents to the knowledge base
        
        Args:
            documents: List of document dictionaries with 'content', 'metadata', and optionally 'id'
        
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        contents = []
        metadatas = []
        ids = []
        
        for doc in documents:
            content = doc.get("content", "")
            if not content or not content.strip():
                continue
            
            contents.append(content)
            metadata = doc.get("metadata", {})
            metadata["content_length"] = len(content)
            metadatas.append(metadata)
            
            doc_id = doc.get("id", str(uuid.uuid4()))
            ids.append(doc_id)
        
        if not contents:
            return []
        
        try:
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(contents)} documents to knowledge base")
            return ids
        
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search in the knowledge base
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"type": "funder_info"})
            min_score: Optional minimum similarity score threshold
        
        Returns:
            List of search results with content, metadata, and distance/score
        """
        if not query or not query.strip():
            return []
        
        try:
            # Perform semantic search
            # ChromaDB uses cosine distance (lower is better)
            # We'll convert distance to similarity score (1 - distance)
            where = filter_metadata if filter_metadata else None
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Format results
            formatted_results = []
            
            if results["ids"] and len(results["ids"]) > 0:
                ids = results["ids"][0]
                documents = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0] if "distances" in results else [0.0] * len(ids)
                
                for i, doc_id in enumerate(ids):
                    distance = distances[i] if i < len(distances) else 0.0
                    similarity = 1.0 - distance  # Convert distance to similarity
                    
                    # Apply minimum score filter if specified
                    if min_score is not None and similarity < min_score:
                        continue
                    
                    formatted_results.append({
                        "id": doc_id,
                        "content": documents[i] if i < len(documents) else "",
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "similarity": similarity,
                        "distance": distance
                    })
            
            logger.debug(f"Search returned {len(formatted_results)} results for query: {query[:50]}")
            return formatted_results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            document_id: Document ID
        
        Returns:
            Document dictionary or None if not found
        """
        try:
            results = self.collection.get(ids=[document_id])
            
            if results["ids"] and len(results["ids"]) > 0:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0] if results["documents"] else "",
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    def update_document(
        self,
        document_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a document
        
        Args:
            document_id: Document ID
            content: New content (optional)
            metadata: New metadata (optional, will merge with existing)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing document
            existing = self.get_document(document_id)
            if not existing:
                logger.warning(f"Document not found: {document_id}")
                return False
            
            # Prepare update
            new_content = content if content is not None else existing["content"]
            existing_metadata = existing.get("metadata", {})
            
            if metadata:
                existing_metadata.update(metadata)
            
            existing_metadata["content_length"] = len(new_content)
            
            # Update in ChromaDB (delete and re-add)
            self.collection.delete(ids=[document_id])
            self.collection.add(
                documents=[new_content],
                metadatas=[existing_metadata],
                ids=[document_id]
            )
            
            logger.debug(f"Document updated: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: Document ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            logger.debug(f"Document deleted: {document_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def add_funder_data(
        self,
        funder_name: str,
        funder_data: Dict[str, Any]
    ) -> str:
        """
        Add structured funder data to knowledge base
        
        Args:
            funder_name: Name of the funder
            funder_data: Dictionary containing funder information
        
        Returns:
            Document ID
        """
        # Format funder data as text content
        content_parts = [
            f"Funder: {funder_name}",
            f"Description: {funder_data.get('description', '')}",
            f"Focus Areas: {', '.join(funder_data.get('focus_areas', []))}",
            f"Requirements: {', '.join(funder_data.get('requirements', []))}",
            f"Priorities: {', '.join(funder_data.get('priorities', []))}",
        ]
        
        if funder_data.get("website"):
            content_parts.append(f"Website: {funder_data['website']}")
        
        if funder_data.get("deadlines"):
            content_parts.append(f"Deadlines: {funder_data['deadlines']}")
        
        if funder_data.get("key_decision_makers"):
            content_parts.append(
                f"Key Decision Makers: {', '.join(funder_data['key_decision_makers'])}"
            )
        
        content = "\n".join(content_parts)
        
        metadata = {
            "type": "funder_data",
            "funder_name": funder_name,
            "source": funder_data.get("source", "unknown"),
            "updated_at": funder_data.get("updated_at", "")
        }
        
        return self.add_document(
            content=content,
            metadata=metadata,
            document_id=f"funder_{funder_name.lower().replace(' ', '_')}"
        )
    
    def search_funders(
        self,
        query: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for funder information
        
        Args:
            query: Search query
            n_results: Number of results
        
        Returns:
            List of funder-related documents
        """
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"type": "funder_data"}
        )
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample documents to analyze
            sample = self.collection.get(limit=min(100, count))
            
            types = {}
            if sample.get("metadatas"):
                for metadata in sample["metadatas"]:
                    doc_type = metadata.get("type", "unknown")
                    types[doc_type] = types.get(doc_type, 0) + 1
            
            return {
                "total_documents": count,
                "document_types": types,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory)
            }
        
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "total_documents": 0,
                "document_types": {},
                "error": str(e)
            }
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self._embedding_function,
                metadata={"description": "Funder knowledge and research data"}
            )
            logger.info(f"Collection '{self.collection_name}' cleared")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

