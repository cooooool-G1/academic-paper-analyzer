"""Large Language Model Service"""

import openai
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Interface with OpenAI GPT models"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """Initialize LLM service"""
        openai.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_summary(self, text: str, max_tokens: int = 200) -> str:
        """Generate summary of text"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant that summarizes research papers."},
                    {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""
    
    def answer_question(self, context: str, question: str) -> str:
        """Answer question based on context"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant. Answer questions based on the provided context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return ""
    
    def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic assistant. Extract key points as a bulleted list."},
                    {"role": "user", "content": f"Extract the key points from the following text:\n\n{text}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            content = response.choices[0].message.content
            # Parse bullet points
            points = [line.strip('- ') for line in content.split('\n') if line.strip().startswith('-')]
            return points
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def classify_topic(self, text: str, topics: List[str] = None) -> str:
        """Classify text into topic categories"""
        try:
            default_topics = [
                "Machine Learning", "Deep Learning", "Natural Language Processing",
                "Computer Vision", "Reinforcement Learning", "Data Mining",
                "Knowledge Graphs", "Information Retrieval", "Other"
            ]
            topics = topics or default_topics
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a research paper classifier. Classify papers into one of these categories: {', '.join(topics)}. Return only the category name."},
                    {"role": "user", "content": f"Classify this paper:\n\n{text[:1000]}"}
                ],
                max_tokens=50,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error classifying topic: {str(e)}")
            return "Other"
