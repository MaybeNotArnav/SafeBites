# backend/app/routers/dish_router.py
"""
DISH ROUTER
APIs implemented:
1. POST   /dishes/               → Create a new dish
2. GET    /dishes/{dish_id}      → Get dish by ID
3. GET    /dishes/               → Get all dishes
4. GET    /dishes/filter         → Filter dishes by exclude_allergens
5. PUT    /dishes/{dish_id}      → Update a dish
6. DELETE /dishes/{dish_id}      → Delete a dish
"""
from fastapi import APIRouter, Query
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

@router.get("/filter", response_model=List[DishOut])
async def filter_dishes(exclude_allergens: Optional[str] = Query(None), restaurant: Optional[str] = None):
    """
    exclude_allergens: comma-separated list e.g. peanuts,gluten
    returns dishes that do NOT contain any of the excluded allergens
    optional restaurant filter is supported
    """
    query = {}
    if restaurant:
        query["restaurant"] = restaurant
    # if no exclude list -> return all (subject to restaurant filter)
    if not exclude_allergens:
        return await dish_service.list_dishes(query)

    exclude_list = [a.strip().lower() for a in exclude_allergens.split(",") if a.strip()]
    # fetch dishes matching restaurant (if provided)
    docs = await dish_service.list_dishes(query)
    safe = []
    for d in docs:
        allergens = [a.lower() for a in d.get("explicit_allergens", [])]
        if not set(allergens) & set(exclude_list):
            safe.append(d)
    return safe

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
