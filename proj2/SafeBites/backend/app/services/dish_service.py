from ..db import db
from bson import ObjectId
from fastapi import HTTPException

def _to_out(doc):
    doc["_id"] = str(doc["_id"])
    return doc

async def create_dish(data):
    doc = data.model_dump()
    doc["availability"] = doc.get("availability", True)
    res = await db.dishes.insert_one(doc)
    created = await db.dishes.find_one({"_id": res.inserted_id})
    return _to_out(created)

async def list_dishes(filter_query: dict):
    docs = await db.dishes.find(filter_query).to_list(length=200)
    return [_to_out(d) for d in docs]

async def get_dish(dish_id: str):
    doc = await db.dishes.find_one({"_id": ObjectId(dish_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Dish not found")
    return _to_out(doc)

async def update_dish(dish_id: str, update_data: dict):
    res = await db.dishes.update_one({"_id": ObjectId(dish_id)}, {"$set": update_data})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    updated = await db.dishes.find_one({"_id": ObjectId(dish_id)})
    return _to_out(updated)

async def delete_dish(dish_id: str):
    res = await db.dishes.delete_one({"_id": ObjectId(dish_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
