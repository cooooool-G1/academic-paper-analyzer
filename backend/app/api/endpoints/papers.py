"""Paper Management Endpoints"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import aiofiles
import hashlib
from pathlib import Path
import uuid

from app.database import get_db
from app.models.paper import Paper
from app.schemas import PaperResponse, PaperListResponse
from app.services.pdf_parser import PDFParser
from app.services.text_processor import TextProcessor
from app.services.embeddings import EmbeddingService
from app.services.vector_db import VectorDBService
from app.config import get_settings

router = APIRouter()
settings = get_settings()
pdf_parser = PDFParser()
text_processor = TextProcessor()
embedding_service = EmbeddingService()
vector_db_service = VectorDBService()


@router.post("/upload")
async def upload_paper(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a PDF paper"""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = Path(settings.upload_dir) / f"{file_id}.pdf"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Check if file already exists
        existing_paper = db.query(Paper).filter(Paper.file_hash == file_hash).first()
        if existing_paper:
            raise HTTPException(status_code=400, detail="This paper has already been uploaded")
        
        # Extract metadata and text
        metadata = pdf_parser.extract_metadata(str(file_path))
        full_text = pdf_parser.extract_text(str(file_path))
        abstract = pdf_parser.extract_abstract(full_text)
        keywords = pdf_parser.extract_keywords(full_text)
        sections = pdf_parser.extract_sections(full_text)
        
        # Create paper record
        paper = Paper(
            user_id="00000000-0000-0000-0000-000000000000",  # Default user for now
            title=file.filename.replace(".pdf", ""),
            abstract=abstract,
            file_path=str(file_path),
            file_size=len(content),
            file_hash=file_hash,
            full_text=full_text[:10000],  # Store first 10000 chars
            keywords=keywords,
            sections=sections,
            processing_status="pending"
        )
        
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        # Generate embeddings asynchronously
        # For now, do it synchronously
        try:
            embedding = embedding_service.embed_combined(
                paper.title,
                abstract,
                keywords
            )
            embedding_id = vector_db_service.add_embedding(
                str(paper.id),
                embedding.tolist(),
                {"title": paper.title, "abstract": abstract}
            )
            
            paper.embedding_id = embedding_id
            paper.is_processed = True
            paper.is_indexed = True
            paper.processing_status = "completed"
            db.commit()
        except Exception as e:
            paper.processing_status = "failed"
            paper.error_message = str(e)
            db.commit()
        
        return {"status": "success", "paper_id": str(paper.id), "message": "Paper uploaded successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading paper: {str(e)}")


@router.get("/list", response_model=PaperListResponse)
async def list_papers(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """List all papers with pagination"""
    try:
        total = db.query(Paper).count()
        offset = (page - 1) * page_size
        papers = db.query(Paper).offset(offset).limit(page_size).all()
        
        return PaperListResponse(
            total=total,
            page=page,
            page_size=page_size,
            papers=papers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching papers: {str(e)}")


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str, db: Session = Depends(get_db)):
    """Get paper details"""
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        return paper
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching paper: {str(e)}")


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str, db: Session = Depends(get_db)):
    """Delete a paper"""
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Delete file
        file_path = Path(paper.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete from vector database
        if paper.embedding_id:
            vector_db_service.delete_embedding(paper.embedding_id)
        
        # Delete from database
        db.delete(paper)
        db.commit()
        
        return {"status": "success", "message": "Paper deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting paper: {str(e)}")
