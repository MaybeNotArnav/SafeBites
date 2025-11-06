from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

class AllergenInfo(BaseModel):
    allergen: str
    confidence: Optional[float] = None
    why: Optional[str] = None

class DishCreate(BaseModel):
    restaurant_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    price: float
    explicit_allergens: Optional[List[Union[str, AllergenInfo]]] = Field(default_factory=list)
    nutrition_facts : Optional[Dict[str, Any]] = None
    availability: Optional[bool] = True

class DishUpdate(BaseModel):
    restaurant_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    price: Optional[float] = None
    explicit_allergens: Optional[List[Union[str, AllergenInfo]]] = None
    nutrition_facts: Optional[Dict[str, Any]] = None
    availability: Optional[bool] = None



class DishOut(BaseModel):
    id: str = Field(..., alias="_id")
    restaurant_id: str
    name: str
    description: Optional[str]
    ingredients: List[str]
    price: float
    explicit_allergens: Optional[List[Union[str, AllergenInfo]]] = []
    nutrition_facts : Optional[Dict[str, Any]] = None
    availability: bool = True
    # ALWAYS boolean now
    safe_for_user: bool
