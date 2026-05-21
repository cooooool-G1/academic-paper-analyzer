"""Search Service"""

from typing import List, Dict, Tuple
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDBService
from app.database import SessionLocal
from app.models.paper import Paper
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """Search for papers using semantic similarity"""
    
    def __init__(self):
        """Initialize search service"""
        self.embedding_service = EmbeddingService()
        self.vector_db_service = VectorDBService()
    
    def search_papers(self, query: str, limit: int = 10, threshold: float = 0.3) -> List[Dict]:
        """Search papers by semantic similarity"""
        try:
            # Embed query
            query_embedding = self.embedding_service.embed_text(query)
            
            # Search in vector database
            results = self.vector_db_service.search(
                query_embedding=query_embedding.tolist(),
                limit=limit,
                threshold=threshold
            )
            
            # Fetch paper details from database
            db = SessionLocal()
            papers = []
            for paper_id, score in results:
                paper = db.query(Paper).filter(Paper.id == paper_id).first()
                if paper:
                    papers.append({
                        "id": str(paper.id),
                        "title": paper.title,
                        "abstract": paper.abstract,
                        "keywords": paper.keywords,
                        "similarity_score": float(score),
                        "category": paper.category
                    })
            db.close()
            
            return sorted(papers, key=lambda x: x['similarity_score'], reverse=True)
        except Exception as e:
            logger.error(f"Error searching papers: {str(e)}")
            return []
    
    def find_related_papers(self, paper_id: str, limit: int = 5) -> List[Dict]:
        """Find papers related to a given paper"""
        try:
            db = SessionLocal()
            paper = db.query(Paper).filter(Paper.id == paper_id).first()
            db.close()
            
            if not paper:
                return []
            
            # Create search query from paper title and abstract
            query = f"{paper.title} {paper.abstract}"
            
            # Search for similar papers
            results = self.search_papers(query, limit=limit + 1, threshold=0.2)
            
            # Remove the paper itself from results
            results = [r for r in results if r["id"] != str(paper_id)]
            
            return results[:limit]
        except Exception as e:
            logger.error(f"Error finding related papers: {str(e)}")
            return []
