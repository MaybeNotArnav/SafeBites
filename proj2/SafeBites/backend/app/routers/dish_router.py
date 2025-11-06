from fastapi import APIRouter, Query
from typing import Optional, List
from ..models.dish_model import DishCreate, DishUpdate, DishOut
from ..services import dish_service

router = APIRouter(prefix="/dishes", tags=["dishes"])

@router.post("/{restaurant_id}", response_model=DishOut, status_code=201)
def create_dish(restaurant_id:str, payload: DishCreate):
    payload.restaurant_id = restaurant_id
    return dish_service.create_dish(restaurant_id, payload)

@router.get("/", response_model=List[DishOut])
def list_dishes(
    restaurant: Optional[str] = None,
    tags: Optional[str] = Query(None),
    user_id: Optional[str] = None
):
    """
    Returns all dishes and ALWAYS includes safe_for_user (True/False).
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
    return dish_service.get_dish(dish_id, user_id=user_id)

@router.put("/{dish_id}", response_model=DishOut)
def update_dish(dish_id: str, payload: DishUpdate):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return dish_service.update_dish(dish_id, data)

@router.delete("/{dish_id}")
def delete_dish(dish_id: str):
    dish_service.delete_dish(dish_id)
    return {"detail": "deleted"}
