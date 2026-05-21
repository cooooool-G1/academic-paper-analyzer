"""API Routes"""

from fastapi import APIRouter
from app.api.endpoints import papers, search, health

router = APIRouter()

# Include endpoint routers
router.include_router(papers.router, prefix="/papers", tags=["papers"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(health.router, prefix="/health", tags=["health"])
