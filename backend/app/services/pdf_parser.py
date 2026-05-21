"""PDF Parsing Service"""

import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract text and metadata from PDF files"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract full text from PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def extract_metadata(self, pdf_path: str) -> Dict:
        """Extract metadata from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata
                return {
                    "title": metadata.get("Title", ""),
                    "author": metadata.get("Author", ""),
                    "subject": metadata.get("Subject", ""),
                    "creator": metadata.get("Creator", ""),
                    "producer": metadata.get("Producer", ""),
                    "creation_date": metadata.get("CreationDate"),
                    "modification_date": metadata.get("ModDate"),
                    "pages": len(pdf.pages)
                }
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {str(e)}")
            return {}
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract major sections from paper text"""
        sections = {
            "abstract": "",
            "introduction": "",
            "methodology": "",
            "results": "",
            "discussion": "",
            "conclusion": "",
            "references": ""
        }
        
        section_patterns = {
            "abstract": r"(?:ABSTRACT|Abstract)[\s\n]+(.*?)(?=(?:1\.|INTRODUCTION|Introduction|1\s))",
            "introduction": r"(?:1\.?\s+)?(?:INTRODUCTION|Introduction)[\s\n]+(.*?)(?=(?:2\.|METHODOLOGY|METHOD|Related Work))",
            "methodology": r"(?:2\.?\s+)?(?:METHODOLOGY|METHOD|METHODS)[\s\n]+(.*?)(?=(?:3\.|RESULTS|EXPERIMENTS))",
            "results": r"(?:3\.?\s+)?(?:RESULTS|EXPERIMENTS|EVALUATION)[\s\n]+(.*?)(?=(?:4\.|DISCUSSION|CONCLUSION))",
            "discussion": r"(?:4\.?\s+)?(?:DISCUSSION)[\s\n]+(.*?)(?=(?:5\.|CONCLUSION|CONCLUSION))",
            "conclusion": r"(?:5\.?\s+)?(?:CONCLUSION|CONCLUSIONS)[\s\n]+(.*?)(?=(?:REFERENCES|BIBLIOGRAPHY))",
            "references": r"(?:REFERENCES|BIBLIOGRAPHY)[\s\n]+(.*?)$"
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()[:2000]  # Limit to 2000 chars
        
        return {k: v for k, v in sections.items() if v}  # Remove empty sections
    
    def extract_abstract(self, text: str) -> str:
        """Extract abstract from paper"""
        pattern = r"(?:ABSTRACT|Abstract)[\s\n]+(.*?)(?=(?:1\.|INTRODUCTION|Introduction|KEYWORDS))"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: return first 500 characters
        return text[:500]
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from paper"""
        pattern = r"(?:KEYWORDS|Keywords)[:=]?\s*([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            keywords_text = match.group(1)
            keywords = [k.strip() for k in keywords_text.split([",", ";"][0])]
            return keywords[:10]  # Limit to 10 keywords
        return []
