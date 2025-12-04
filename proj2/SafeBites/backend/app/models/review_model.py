"""
Pydantic models for dish reviews.

Includes input schemas and output schemas used by review endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional

class ReviewCreate(BaseModel):
    dish_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    dish_id: str
    rating: int
    comment: Optional[str]
    created_at: str
    updated_at: str
