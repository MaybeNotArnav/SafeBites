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

@router.post("/", response_model=DishOut, status_code=201)
async def create_dish(payload: DishCreate):
    return await dish_service.create_dish(payload)

@router.get("/", response_model=List[DishOut])
async def list_dishes(restaurant: Optional[str] = None, tags: Optional[str] = Query(None)):
    query = {}
    if restaurant:
        query["restaurant"] = restaurant
    if tags:
        query["ingredients"] = {"$in": tags.split(",")}
    return await dish_service.list_dishes(query)

@router.get("/{dish_id}", response_model=DishOut)
async def get_dish(dish_id: str):
    return await dish_service.get_dish(dish_id)

@router.put("/{dish_id}", response_model=DishOut)
async def update_dish(dish_id: str, payload: DishUpdate):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return await dish_service.update_dish(dish_id, data)

@router.delete("/{dish_id}")
async def delete_dish(dish_id: str):
    await dish_service.delete_dish(dish_id)
    return {"detail": "deleted"}
