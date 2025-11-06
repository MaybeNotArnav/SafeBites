"""
Defines Pydantic models for handling restaurant and menu-related data
in the SafeBites backend.

Models:

- RestaurantBase: Basic restaurant information.
- RestaurantCreate: Schema for creating a new restaurant.
- RestaurantUpdate: Schema for updating an existing restaurant.
- RestaurantInDB: Database representation of a restaurant.
- PriceFilter: Filter for dish prices.
- IngredientFilter: Include/exclude ingredient filters.
- AllergenFilter: Exclude allergen filters.
- NutritionFilter: Nutritional constraints for dishes.
- DishFilterModel: Aggregates all dish filters.
- DishValidationResult: Outcome of validating a dish against filters.
- MenuQueryResults: Result of a menu search query.
- MenuResultResponse: Structured response for menu retrieval.

These models are used throughout the backend for validation, data exchange,
and API responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .dish_info_model import DishData

class RestaurantBase(BaseModel):
    """
    Represents basic information about a restaurant.

    Attributes:
        name (str): The name of the restaurant.
        location (str): The geographical location of the restaurant.
        cuisine (Optional[List[str]]): A list of cuisines the restaurant serves.
        rating (Optional[float]): The restaurant's rating between 0 and 5.
    """
    name:str
    location:str
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantCreate(RestaurantBase):
    """
    Represents the schema used for creating a new restaurant entry.

    Attributes:
        name (str): The name of the restaurant.
        location (str): The geographical location of the restaurant.
        cuisine (Optional[List[str]]): A list of cuisines the restaurant serves.
        rating (Optional[float]): The restaurant's rating between 0 and 5.
    """
    name:str
    location:str
    cuisine:Optional[List[str]]
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantUpdate(BaseModel):
    """
    Represents the schema used for updating an existing restaurant record.

    Attributes:
        name (Optional[str]): Updated name of the restaurant.
        location (Optional[str]): Updated location.
        cuisine (Optional[List[str]]): Updated list of cuisines.
        rating (Optional[float]): Updated rating (0–5).
    """
    name:Optional[str] = None
    location:Optional[str] = None
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = None

class RestaurantInDB(RestaurantBase):
    """
    Represents a restaurant record stored in the database.

    Attributes:
        id (str): The unique identifier for the restaurant (aliased as `_id` in the database).
    """
    id:str = Field(alias="_id")

    class Config:
        populate_by_name = True


class PriceFilter(BaseModel):
    """
    Represents filtering criteria for dish prices.

    Attributes:
        min (float): The minimum price threshold.
        max (float): The maximum price threshold.
    """
    min:float = Field(default=0)
    max:float = Field(default=float("inf"))

class IngredientFilter(BaseModel):
    """
    Represents ingredient-based filters for dishes.

    Attributes:
        include (List[str]): Ingredients that must be included.
        exclude (List[str]): Ingredients that must be excluded.
    """
    include: List[str] = Field(default_factory=list)
    exclude : List[str] = Field(default_factory=list)

class AllergenFilter(BaseModel):
    """
    Represents allergen-based filters for dishes.

    Attributes:
        exclude (List[str]): Allergens that should be excluded from dishes.
    """
    exclude:List[str] = Field(default_factory=list)

class NutritionFilter(BaseModel):
    """
    Represents nutritional filters to refine dish recommendations.

    Attributes:
        max_calories (Optional[float]): Maximum allowed calorie content.
        min_protein (Optional[float]): Minimum required protein content.
        max_fat (Optional[float]): Maximum allowed fat content.
        max_carbs (Optional[float]): Maximum allowed carbohydrate content.
    """
    max_calories:Optional[float] = None
    min_protein: Optional[float] = None
    max_fat : Optional[float] = None
    max_carbs : Optional[float] = None

class DishFilterModel(BaseModel):
    """
    Represents a comprehensive model for applying multiple filters
    (price, ingredients, allergens, and nutrition) to dish queries.

    Attributes:
        price (PriceFilter): Price-based filter.
        ingredients (IngredientFilter): Ingredient inclusion/exclusion filter.
        allergens (AllergenFilter): Allergen exclusion filter.
        nutrition (NutritionFilter): Nutritional limits filter.
    """
    price : PriceFilter = Field(default_factory=PriceFilter)
    ingredients: IngredientFilter = Field(default_factory=IngredientFilter)
    allergens: AllergenFilter = Field(default_factory=AllergenFilter)
    nutrition: NutritionFilter = Field(default_factory=NutritionFilter)

class DishValidationResult(BaseModel):
    """
    Represents the result of dish validation against given filters.

    Attributes:
        dish_id (str): Unique identifier for the dish.
        include (bool): Whether the dish meets the filter criteria.
        reason (Optional[str]): Explanation if the dish was excluded.
    """
    dish_id:str
    include:bool
    reason : Optional[str] = None

class MenuQueryResults(BaseModel):
    """
    Represents the result of a menu query containing matched dishes.

    Attributes:
        query (str): The user's search query.
        dishes (List[Dict[str, Any]]): A list of matching dishes with their details.
    """
    query: str
    dishes: List[Dict[str,Any]] = Field(default_factory=list)

class MenuResultResponse(BaseModel):
    """
    Represents a structured response for menu retrieval queries.

    Attributes:
        menu_results (Dict[str, List[DishData]]): Mapping of query strings to lists of matching dishes.
    """
    menu_results: Dict[str, List[DishData]] = Field(default_factory=dict)
