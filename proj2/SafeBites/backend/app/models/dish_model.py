from pydantic import BaseModel, Field
from typing import List, Optional

class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    restaurant: str
    price: float
    explicit_allergens: List[str] = Field(default_factory=list)
    availability: Optional[bool] = True

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
    explicit_allergens: List[str] = Field(default_factory=list)
    availability: bool = True
    safe_for_user: Optional[bool] = None
