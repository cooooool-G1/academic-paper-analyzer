"""Celery Tasks for Async Processing"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "academic_paper_analyzer",
    broker=settings.redis_url,
    backend=settings.redis_url
)


@celery_app.task
def process_paper(paper_id: str):
    """Process uploaded paper asynchronously"""
    from app.database import SessionLocal
    from app.models.paper import Paper
    from app.services.embeddings import EmbeddingService
    from app.services.vector_db import VectorDBService
    
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            return {"status": "error", "message": "Paper not found"}
        
        # Generate embeddings
        embedding_service = EmbeddingService()
        vector_db_service = VectorDBService()
        
        embedding = embedding_service.embed_combined(
            paper.title,
            paper.abstract or "",
            paper.keywords or []
        )
        
        embedding_id = vector_db_service.add_embedding(
            str(paper.id),
            embedding.tolist(),
            {"title": paper.title}
        )
        
        paper.embedding_id = embedding_id
        paper.is_processed = True
        paper.is_indexed = True
        paper.processing_status = "completed"
        db.commit()
        
        return {"status": "success", "paper_id": str(paper.id)}
    except Exception as e:
        paper.processing_status = "failed"
        paper.error_message = str(e)
        db.commit()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
