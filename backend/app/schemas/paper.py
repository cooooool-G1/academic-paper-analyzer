"""Paper Schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PaperCreate(BaseModel):
    """Paper creation schema"""
    title: str
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None


class PaperUpdate(BaseModel):
    """Paper update schema"""
    title: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    category: Optional[str] = None


class PaperResponse(BaseModel):
    """Paper response schema"""
    id: UUID
    title: str
    abstract: Optional[str] = None
    authors: Optional[List[str]] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    keywords: Optional[List[str]] = None
    topics: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    is_processed: bool
    is_indexed: bool
    processing_status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    """Paper list response schema"""
    total: int
    page: int
    page_size: int
    papers: List[PaperResponse]
