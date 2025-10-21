from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..db import db
from ..models.dish_model import DishCreate, DishUpdate, DishOut
from bson import ObjectId

router = APIRouter(prefix="/dishes", tags=["dishes"])

def _to_out(doc):
    doc["_id"] = str(doc["_id"])
    return doc

@router.post("/", status_code=201)
async def create_dish(payload: DishCreate):
    doc = payload.model_dump()
    doc["availability"] = True
    res = await db.dishes.insert_one(doc)
    created = await db.dishes.find_one({"_id": res.inserted_id})
    return _to_out(created)

@router.get("/", response_model=List[DishOut])
async def list_dishes(restaurant: Optional[str] = None, tags: Optional[str] = Query(None)):
    q = {}
    if restaurant:
        q["restaurant"] = restaurant
    if tags:
        tags_set = set(tags.split(","))
        q["ingredients"] = {"$in": list(tags_set)}
    docs = await db.dishes.find(q).to_list(length=200)
    return [_to_out(d) for d in docs]

@router.get("/{dish_id}", response_model=DishOut)
async def get_dish(dish_id: str):
    doc = await db.dishes.find_one({"_id": ObjectId(dish_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Dish not found")
    return _to_out(doc)

@router.put("/{dish_id}", response_model=DishOut)
async def update_dish(dish_id: str, payload: DishUpdate):
    update_doc = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields to update")
    res = await db.dishes.update_one({"_id": ObjectId(dish_id)}, {"$set": update_doc})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    doc = await db.dishes.find_one({"_id": ObjectId(dish_id)})
    return _to_out(doc)

@router.delete("/{dish_id}")
async def delete_dish(dish_id: str):
    res = await db.dishes.delete_one({"_id": ObjectId(dish_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"detail": "deleted"}
