from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .dish_info_model import DishData

class RestaurantBase(BaseModel):
    name:str
    location:str
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantCreate(RestaurantBase):
    name:str
    location:str
    cuisine:Optional[List[str]]
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantUpdate(BaseModel):
    name:Optional[str] = None
    location:Optional[str] = None
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = None

class RestaurantInDB(RestaurantBase):
    id:str = Field(alias="_id")

    class Config:
        populate_by_name = True


class PriceFilter(BaseModel):
    min:float = Field(default=0)
    max:float = Field(default=float("inf"))

class IngredientFilter(BaseModel):
    include: List[str] = Field(default_factory=list)
    exclude : List[str] = Field(default_factory=list)

class AllergenFilter(BaseModel):
    exclude:List[str] = Field(default_factory=list)

class NutritionFilter(BaseModel):
    max_calories:Optional[float] = None
    min_protein: Optional[float] = None
    max_fat : Optional[float] = None
    max_carbs : Optional[float] = None

class DishFilterModel(BaseModel):
    price : PriceFilter = Field(default_factory=PriceFilter)
    ingredients: IngredientFilter = Field(default_factory=IngredientFilter)
    allergens: AllergenFilter = Field(default_factory=AllergenFilter)
    nutrition: NutritionFilter = Field(default_factory=NutritionFilter)

class DishValidationResult(BaseModel):
    dish_id:str
    include:bool
    reason : Optional[str] = None

class MenuQueryResults(BaseModel):
    query: str
    dishes: List[Dict[str,Any]] = Field(default_factory=list)

class MenuResultResponse(BaseModel):
    menu_results: Dict[str, List[DishData]] = Field(default_factory=dict)