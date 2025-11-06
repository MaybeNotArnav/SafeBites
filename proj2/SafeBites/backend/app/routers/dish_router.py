"""
Defines API endpoints for managing dishes in the SafeBites backend.

Endpoints include:
    - POST /dishes/{restaurant_id}: Create a new dish for a specific restaurant.
    - GET /dishes: Retrieve all dishes (with optional filters by restaurant, ingredients, or user safety).
    - GET /dishes/filter: Retrieve dishes filtered by allergens and restaurant.
    - GET /dishes/{dish_id}: Retrieve a single dish by its ID.
    - PUT /dishes/{dish_id}: Update details of an existing dish.
    - DELETE /dishes/{dish_id}: Delete a dish by ID.
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from ..models.dish_model import DishCreate, DishUpdate, DishOut
from ..services import dish_service

router = APIRouter(prefix="/dishes", tags=["dishes"])
"""
This module defines API endpoints for managing dishes within a restaurant.

Endpoints:
    - POST /dishes/{restaurant_id}: Create a new dish for a specific restaurant.
    - GET /dishes: Retrieve all dishes (optionally filtered by restaurant, tags, or user safety).
    - GET /dishes/filter: Retrieve dishes filtered by allergens and restaurant.
    - GET /dishes/{dish_id}: Retrieve a single dish by its ID.
    - PUT /dishes/{dish_id}: Update details of an existing dish.
    - DELETE /dishes/{dish_id}: Delete a dish by ID.
"""

@router.post("/{restaurant_id}", response_model=DishOut, status_code=201)
def create_dish(restaurant_id:str, payload: DishCreate):
    """
    Create a new dish for a specific restaurant.

    Args:
        restaurant_id (str): The ID of the restaurant to which the dish belongs.
        payload (DishCreate): The data required to create the dish (name, ingredients, price, etc.).

    Returns:
        DishOut: The created dish object.
    """
    payload.restaurant_id = restaurant_id
    return dish_service.create_dish(restaurant_id, payload)

@router.get("/", response_model=List[DishOut])
def list_dishes(
    restaurant: Optional[str] = None,
    tags: Optional[str] = Query(None),
    user_id: Optional[str] = None
):
    """
    Retrieve all dishes with optional filters.

    The result always includes the `safe_for_user` field, indicating
    whether each dish is considered safe for the given user based on allergens.

    Args:
        restaurant (Optional[str]): Filter by restaurant ID.
        tags (Optional[str]): Comma-separated list of ingredients to match.
        user_id (Optional[str]): User ID to evaluate allergen safety.

    Returns:
        List[DishOut]: A list of dish objects matching the criteria.
    """
    query = {}
    if restaurant:
        query["restaurant_id"] = restaurant
    if tags:
        query["ingredients"] = {"$in": tags.split(",")}
    return dish_service.list_dishes(query, user_id=user_id)

@router.get("/filter", response_model=List[DishOut])
def filter_dishes(
    exclude_allergens: Optional[str] = Query(None),
    restaurant: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Retrieve dishes while filtering out those that contain specified allergens.

    Args:
        exclude_allergens (Optional[str]): Comma-separated list of allergens to exclude.
        restaurant (Optional[str]): Filter by restaurant ID.
        user_id (Optional[str]): Optional user ID to further refine allergen filtering.

    Returns:
        List[DishOut]: List of dishes that do not contain the specified allergens.
    """
    query = {}
    if restaurant:
        query["restaurant_id"] = restaurant
    docs = dish_service.list_dishes(query, user_id=user_id)

    if not exclude_allergens:
        return docs

    exclude_list = [a.strip().lower() for a in exclude_allergens.split(",") if a.strip()]
    safe = []
    for d in docs:
        dish_all = [a.lower() for a in d.get("explicit_allergens", [])]
        if not set(dish_all) & set(exclude_list):
            safe.append(d)
    return safe

@router.get("/{dish_id}", response_model=DishOut)
def get_dish(dish_id: str, user_id: Optional[str] = None):
    """
    Retrieve details of a specific dish by its ID.

    Args:
        dish_id (str): The unique identifier of the dish.
        user_id (Optional[str]): Optional user ID to include allergen safety info.

    Returns:
        DishOut: The dish details if found.
    """
    return dish_service.get_dish(dish_id, user_id=user_id)

@router.put("/{dish_id}", response_model=DishOut)
def update_dish(dish_id: str, payload: DishUpdate):
    """
    Update an existing dish’s details.

    Args:
        dish_id (str): The ID of the dish to update.
        payload (DishUpdate): The fields to update (only non-null values are applied).

    Returns:
        DishOut: The updated dish object.
    """
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return dish_service.update_dish(dish_id, data)

@router.delete("/{dish_id}")
def delete_dish(dish_id: str):
    """
    Delete a dish by its ID.

    Args:
        dish_id (str): The unique identifier of the dish to delete.

    Returns:
        dict: A confirmation message indicating successful deletion.
    """
    dish_service.delete_dish(dish_id)
    return {"detail": "deleted"}
