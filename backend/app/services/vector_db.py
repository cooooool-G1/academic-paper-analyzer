"""Vector Database Service"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional, Tuple
import logging
import uuid

logger = logging.getLogger(__name__)

client = None


async def init_vector_db():
    """Initialize vector database"""
    global client
    from app.config import get_settings
    settings = get_settings()
    try:
        client = QdrantClient(url=settings.qdrant_url)
        # Try to get collection info, create if not exists
        try:
            client.get_collection(settings.qdrant_collection_name)
            logger.info(f"Collection {settings.qdrant_collection_name} already exists")
        except Exception:
            logger.info(f"Creating collection {settings.qdrant_collection_name}")
            client.recreate_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.vector_size,
                    distance=Distance.COSINE
                )
            )
        logger.info("Vector database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector database: {str(e)}")
        raise


class VectorDBService:
    """Manage vector embeddings in Qdrant"""
    
    def __init__(self, collection_name: str = "academic_papers"):
        """Initialize vector DB service"""
        from app.config import get_settings
        settings = get_settings()
        self.collection_name = collection_name
        self.client = QdrantClient(url=settings.qdrant_url)
    
    def add_embedding(self, paper_id: str, embedding: List[float], metadata: Dict = None) -> bool:
        """Add embedding to vector database"""
        try:
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=hash(point_id) % (2**63),
                vector=embedding,
                payload={
                    "paper_id": paper_id,
                    **(metadata or {})
                }
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Added embedding for paper {paper_id}")
            return point_id
        except Exception as e:
            logger.error(f"Error adding embedding: {str(e)}")
            raise
    
    def search(self, query_embedding: List[float], limit: int = 10, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """Search for similar embeddings"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=threshold
            )
            papers = []
            for result in results:
                paper_id = result.payload.get("paper_id")
                score = result.score
                if paper_id:
                    papers.append((paper_id, score))
            return papers
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []
    
    def delete_embedding(self, point_id: str) -> bool:
        """Delete embedding from vector database"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_id
            )
            logger.info(f"Deleted embedding {point_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": info.name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
