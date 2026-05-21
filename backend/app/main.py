"""FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api import router as api_router
from app.database import engine, Base
from app.services.vector_db import init_vector_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Application startup")
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Initialize Qdrant collection
    await init_vector_db()
    
    yield
    
    # Shutdown
    print("Application shutdown")


app = FastAPI(
    title="Academic Paper Analyzer",
    description="Intelligent analysis and knowledge discovery system for research papers",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Academic Paper Analyzer API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }
