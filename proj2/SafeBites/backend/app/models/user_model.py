from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    allergen_preferences: List[str] = Field(default_factory=list)

class UserUpdate(BaseModel):
    name: Optional[str]
    allergen_preferences: Optional[List[str]]

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    allergen_preferences: List[str] = []
