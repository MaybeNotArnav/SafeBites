from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    username: str
    # Limit password to 3–72 characters
    password: str = Field(..., min_length=3, max_length=72)
    allergen_preferences: List[str] = Field(default_factory=list)

class UserUpdate(BaseModel):
    name: Optional[str]
    allergen_preferences: Optional[List[str]]

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    username: str
    allergen_preferences: List[str] = []
