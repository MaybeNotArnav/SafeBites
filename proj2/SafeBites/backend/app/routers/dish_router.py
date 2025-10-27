"""
DISH ROUTER
APIs implemented:
1. POST   /dishes/               → Create a new dish
2. GET    /dishes/{dish_id}      → Get dish by ID
3. GET    /dishes/               → Get all dishes
4. PUT    /dishes/{dish_id}      → Update a dish
5. DELETE /dishes/{dish_id}      → Delete a dish
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..models.dish_model import DishCreate, DishUpdate, DishOut
from ..services import dish_service

router = APIRouter(prefix="/dishes", tags=["dishes"])

@router.post("/{restaurant_id}", response_model=DishOut, status_code=201)
def create_dish(restaurant_id:str, payload: DishCreate):
    return dish_service.create_dish(restaurant_id, payload)

@router.get("/", response_model=List[DishOut])
def list_dishes(restaurant: Optional[str] = None, tags: Optional[str] = Query(None)):
    query = {}
    if restaurant:
        query["restaurant_id"] = restaurant
    if tags:
        query["ingredients"] = {"$in": tags.split(",")}
    return dish_service.list_dishes(query)

@router.get("/{dish_id}", response_model=DishOut)
def get_dish(dish_id: str):
    return dish_service.get_dish(dish_id)

@router.put("/{dish_id}", response_model=DishOut)
def update_dish(dish_id: str, payload: DishUpdate):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return dish_service.update_dish(dish_id, data)

@router.delete("/{dish_id}")
def delete_dish(dish_id: str):
    dish_service.delete_dish(dish_id)
    return {"detail": "deleted"}
