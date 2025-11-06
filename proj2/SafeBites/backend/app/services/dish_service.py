from ..db import db
from bson import ObjectId
from fastapi import HTTPException
from bson.objectid import ObjectId
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException, ConflictException


def _to_out(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    return doc

def create_dish(restaurant_id: str, dish_create):
    if not dish_create.name or not dish_create.restaurant_id:
        raise BadRequestException(message="Missing required dish fields")
    # enforce unique dish name per restaurant
    existing = db.dishes.find_one({"name": dish_create.name, "restaurant_id": dish_create.restaurant_id})
    if existing:
        raise ConflictException(detail="Dish with same name already exists for this restaurant")

    doc = dish_create.model_dump()
    doc["availability"] = doc.get("availability", True)
    try:
        res = db.dishes.insert_one(doc)
        created = db.dishes.find_one({"_id": res.inserted_id})
        out = _to_out(created)
        out["safe_for_user"] = True  # default
        return out
    except Exception as e:
        raise DatabaseException(message=f"Failed to create dish: {e}")
    

def list_dishes(filter_query: dict, user_id: str = None):
    """
    ALWAYS attach safe_for_user boolean.
    """
    try:
        docs = list(db.dishes.find(filter_query).limit(100))
        print(docs)
        out = []
        user_allergens = []

        # Get user allergens if user_id provided
        if user_id:
            try:
                user_doc = db.users.find_one({"_id": ObjectId(user_id)})
                print(user_doc)
                if user_doc:
                    user_allergens = [a.lower() for a in user_doc.get("allergen_preferences", [])]
            except Exception:
                pass

        for d in docs:
            d_out = _to_out(d)
            dish_all = [a.lower() for a in d_out.get("explicit_allergens", [])]

            if user_allergens:
                d_out["safe_for_user"] = len(set(dish_all) & set(user_allergens)) == 0
            else:
                d_out["safe_for_user"] = True

            out.append(d_out)

        return out
    except Exception as e:
        raise DatabaseException(message=f"Failed to list dishes: {e}")

def get_dish(dish_id: str, user_id: str = None):
    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise NotFoundException(name="Invalid dish id")

    doc = db.dishes.find_one({"_id": obj})
    if not doc:
        raise NotFoundException(name="Dish not found")

    d_out = _to_out(doc)
    dish_all = [a.lower() for a in d_out.get("explicit_allergens", [])]

    if user_id:
        try:
            user_doc = db.users.find_one({"_id": ObjectId(user_id)})
            user_allergens = [a.lower() for a in user_doc.get("allergen_preferences", [])] if user_doc else []
            d_out["safe_for_user"] = len(set(dish_all) & set(user_allergens)) == 0
        except Exception:
            d_out["safe_for_user"] = True
    else:
        d_out["safe_for_user"] = True

    return d_out

def update_dish(dish_id: str, update_data: dict):
    if not update_data:
        raise BadRequestException(message="No fields to update")

    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise NotFoundException(name="Invalid dish id")
    if "name" in update_data or "restaurant" in update_data:
        current = db.dishes.find_one({"_id": obj})
        if not current:
            raise NotFoundException(name="Dish not found")
        new_name = update_data.get("name", current.get("name"))
        new_rest = update_data.get("restaurant", current.get("restaurant"))
        other = db.dishes.find_one({"name": new_name, "restaurant": new_rest, "_id": {"$ne": obj}})
        if other:
            raise ConflictException(detail="Another dish with same name exists in the restaurant")

    res = db.dishes.update_one({"_id": obj}, {"$set": update_data})
    if res.matched_count == 0:
        raise NotFoundException(name="Dish not found")

    updated = db.dishes.find_one({"_id": obj})
    out = _to_out(updated)
    out["safe_for_user"] = True
    return out


def delete_dish(dish_id: str):
    try:
        obj = ObjectId(dish_id)
    except Exception:
        raise NotFoundException(name="Invalid dish id")

    res = db.dishes.delete_one({"_id": obj})
    if res.deleted_count == 0:
        raise NotFoundException(name="Dish not found")

    return {"detail": "deleted"}