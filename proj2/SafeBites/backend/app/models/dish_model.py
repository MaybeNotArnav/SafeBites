from pydantic import BaseModel, Field
from typing import List, Optional

class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[str] = []
    restaurant: str
    price: float = 0.0
    explicit_allergens: List[str] = []

class DishUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    ingredients: Optional[List[str]]
    price: Optional[float]
    explicit_allergens: Optional[List[str]]
    availability: Optional[bool]

class DishOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    description: Optional[str]
    ingredients: List[str]
    restaurant: str
    price: float
    explicit_allergens: List[str] = []
    availability: bool = True
