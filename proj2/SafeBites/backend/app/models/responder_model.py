from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Price(BaseModel):
    value:float
    currency:str = "USD"

class DishResult(BaseModel):
    dish_id:str
    name:str
    price:Optional[Price] = None
    metadata : Optional[Dict[str,Any]] = None

class InformativeInfo(BaseModel):
    type:str
    description:str
    relevant_dishes:Optional[List[str]] = None
    ui_hints:Optional[Dict[str,Any]] = None

class UIHints(BaseModel):
    component:str
    highlight_field: Optional[str] = None

class UnifiedResponse(BaseModel):
    intent: str
    query:str
    results: Optional[List[DishResult]] = None
    Informative_info: Optional[List[InformativeInfo]] = []
    ui_hints: Optional[UIHints] = None