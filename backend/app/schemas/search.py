"""Search Schemas"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID


class SearchRequest(BaseModel):
    """Search request schema"""
    query: str
    limit: int = 10
    threshold: float = 0.3
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Single search result"""
    paper_id: UUID
    title: str
    similarity_score: float
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    total: int
    results: List[SearchResult]
