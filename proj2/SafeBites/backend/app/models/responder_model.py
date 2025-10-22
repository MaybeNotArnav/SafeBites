from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class AllergenInfo(BaseModel):
    allergen:str
    confidence:float
    why:Optional[str]

class NutritionFacts(BaseModel):
    calories: Optional[Dict[str,Any]] = None
    protein : Optional[Dict[str,Any]] = None
    fat : Optional[Dict[str,Any]] = None
    carbohydrates : Optional[Dict[str,Any]] = None
    sugar : Optional[Dict[str,Any]] = None
    fiber : Optional[Dict[str,Any]] = None

class DishResult(BaseModel):
    _id:str
    restaurant_id:str
    name:str
    description:str
    price:Optional[float]
    ingredients:Optional[List[str]] = []
    inferred_allergens: Optional[List[AllergenInfo]] = []
    nutrition_facts : Optional[NutritionFacts] = None
    availability : Optional[bool] = None
    serving_size : Optional[str] = None
    explicit_allergens : Optional[List[str]] = None

class InfoResult(BaseModel):
    dish_name:Optional[str] = None
    requested_info:Optional[Union[str, Dict[str, Any]]] = None
    source_data : Optional[List[Any]] = []

class QueryResponse(BaseModel):
    query : str
    type : str
    result : Union[List[DishResult],InfoResult, Dict[str,str]]


class FinalResponse(BaseModel):
    user_id:str
    session_id:str
    restaurant_id:str
    original_query:str
    responses : List[QueryResponse]
    status : str
    timestamp : str = Field(default_factory=lambda: datetime.utcnow().isoformat())

