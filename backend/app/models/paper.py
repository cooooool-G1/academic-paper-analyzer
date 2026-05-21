"""Paper Model"""

from sqlalchemy import Column, String, DateTime, Text, Integer, Float, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
from app.database import Base


class Paper(Base):
    """Paper model"""
    __tablename__ = "papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Metadata
    title = Column(String(500), nullable=False, index=True)
    abstract = Column(Text)
    authors = Column(ARRAY(String), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    journal = Column(String(255), nullable=True)
    doi = Column(String(255), unique=True, nullable=True, index=True)
    
    # File Info
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Content
    full_text = Column(Text, nullable=True)
    sections = Column(JSON, nullable=True)  # {"introduction": "...", "methodology": "..."}
    keywords = Column(ARRAY(String), nullable=True)
    
    # Analysis Results
    topics = Column(JSON, nullable=True)  # [{"name": "...", "probability": 0.8}]
    category = Column(String(255), nullable=True, index=True)
    summary = Column(Text, nullable=True)
    
    # Vector Embedding
    embedding_id = Column(String(255), nullable=True, index=True)  # Qdrant point ID
    
    # Metadata
    is_processed = Column(Boolean, default=False, index=True)
    is_indexed = Column(Boolean, default=False, index=True)
    processing_status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Paper {self.title}>"
