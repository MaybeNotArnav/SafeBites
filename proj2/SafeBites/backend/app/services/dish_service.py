from ..db import db
from bson import ObjectId
from app.models.exception_model import ResourceNotFound, ConflictError, BadRequest, DatabaseException

def _to_out(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc

async def create_dish(dish_create):
    # basic validation
    if not dish_create.name or not dish_create.restaurant:
        raise BadRequest(detail="Missing required dish fields: name and restaurant")

    # enforce unique (restaurant, name)
    existing = await db.dishes.find_one({"name": dish_create.name, "restaurant": dish_create.restaurant})
    if existing:
        raise ConflictError(detail="Dish with same name already exists for this restaurant")

    doc = dish_create.model_dump()
    doc["availability"] = doc.get("availability", True)
    try:
        res = await db.dishes.insert_one(doc)
        created = await db.dishes.find_one({"_id": res.inserted_id})
        return _to_out(created)
    except Exception as e:
        raise DatabaseException(message=f"Failed to create dish: {e}")

async def list_dishes(filter_query: dict):
    try:
        docs = await db.dishes.find(filter_query).to_list(length=200)
        return [_to_out(d) for d in docs]
    except Exception as e:
        raise DatabaseException(message=f"Failed to list dishes: {e}")

async def get_dish(dish_id: str):
    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid dish id")
    doc = await db.dishes.find_one({"_id": obj})
    if not doc:
        raise ResourceNotFound(detail="Dish not found")
    return _to_out(doc)

async def update_dish(dish_id: str, update_data: dict):
    if not update_data:
        raise BadRequest(detail="No fields to update")
    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid dish id")

    # if updating name+restaurant to collide with existing dish, check conflict
    if "name" in update_data or "restaurant" in update_data:
        # fetch current doc to see resulting combination
        current = await db.dishes.find_one({"_id": obj})
        if not current:
            raise ResourceNotFound(detail="Dish not found")

        new_name = update_data.get("name", current.get("name"))
        new_rest = update_data.get("restaurant", current.get("restaurant"))
        other = await db.dishes.find_one({"name": new_name, "restaurant": new_rest, "_id": {"$ne": obj}})
        if other:
            raise ConflictError(detail="Another dish with same name exists in the restaurant")

    res = await db.dishes.update_one({"_id": obj}, {"$set": update_data})
    if res.matched_count == 0:
        raise ResourceNotFound(detail="Dish not found")
    updated = await db.dishes.find_one({"_id": obj})
    return _to_out(updated)

async def delete_dish(dish_id: str):
    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid dish id")
    res = await db.dishes.delete_one({"_id": obj})
    if res.deleted_count == 0:
        raise ResourceNotFound(detail="Dish not found")
    return
