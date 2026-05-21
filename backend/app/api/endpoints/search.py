"""Search Endpoints"""

from fastapi import APIRouter, Query, HTTPException
from app.services.search import SearchService
from app.schemas import SearchRequest, SearchResponse, SearchResult
from typing import List

router = APIRouter()
search_service = SearchService()


@router.get("/papers")
async def search_papers(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    threshold: float = Query(0.3, ge=0.0, le=1.0)
):
    """Search for papers by semantic similarity"""
    try:
        results = search_service.search_papers(query, limit=limit, threshold=threshold)
        return SearchResponse(
            query=query,
            total=len(results),
            results=[SearchResult(**r) for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching papers: {str(e)}")


@router.get("/related/{paper_id}")
async def get_related_papers(
    paper_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """Get papers related to a specific paper"""
    try:
        results = search_service.find_related_papers(paper_id, limit=limit)
        return {
            "paper_id": paper_id,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding related papers: {str(e)}")
