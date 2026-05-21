"""Text Processing Service"""

import re
import string
from typing import List
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """Clean and preprocess text"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
    
    def _load_stopwords(self) -> set:
        """Load English stopwords"""
        # Common English stopwords
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'as', 'by', 'from', 'up', 'about',
            'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'only', 'same', 'so', 'such', 'no', 'nor',
            'not', 'own', 'its', 'my', 'your', 'our', 'their', 'him', 'her', 'us'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,-]', '', text)
        return text.strip()
    
    def normalize_text(self, text: str) -> str:
        """Normalize text"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def remove_stopwords(self, text: str) -> str:
        """Remove stopwords from text"""
        words = text.lower().split()
        filtered_words = [w for w in words if w not in self.stopwords]
        return ' '.join(filtered_words)
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        text = self.normalize_text(text)
        # Split by whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def preprocess(self, text: str, remove_stopwords: bool = True) -> str:
        """Complete preprocessing pipeline"""
        # Clean
        text = self.clean_text(text)
        # Normalize
        text = self.normalize_text(text)
        # Remove stopwords
        if remove_stopwords:
            text = self.remove_stopwords(text)
        return text
