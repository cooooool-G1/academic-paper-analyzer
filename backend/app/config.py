"""Application Configuration"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://academic_user:academic_password@localhost:5432/academic_db"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    app_env: str = "development"
    debug: bool = True
    
    # File Upload
    max_upload_size: int = 52428800  # 50MB
    allowed_file_types: list = ["pdf"]
    upload_dir: str = "uploads"
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Qdrant Collection
    qdrant_collection_name: str = "academic_papers"
    vector_size: int = 384
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
