"""User Schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """User creation schema"""
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
