"""Business logic for shopping cart operations."""
from datetime import datetime
from typing import Dict, List, Tuple
from bson.objectid import ObjectId
from app.db import db
from app.models.exception_model import BadRequestException, NotFoundException


def _serialize_cart(cart: Dict) -> Dict:
    cart = dict(cart)
    cart["_id"] = str(cart["_id"])
    cart["updated_at"] = cart.get("updated_at", datetime.utcnow())
    serialized_items = []
    for item in cart.get("items", []):
        serialized_item = dict(item)
        serialized_item["dish_id"] = str(serialized_item.get("dish_id"))
        if serialized_item.get("restaurant_id") is not None:
            serialized_item["restaurant_id"] = str(serialized_item["restaurant_id"])
        serialized_item.setdefault("restaurant_name", "Restaurant")
        serialized_items.append(serialized_item)
    cart["items"] = serialized_items
    return cart


def _recalculate(cart: Dict) -> None:
    cart["subtotal"] = round(
        sum(item["price"] * item["quantity"] for item in cart.get("items", [])),
        2,
    )
    cart["updated_at"] = datetime.utcnow()


def _fetch_dish(dish_id: str) -> Dict:
    dish = None
    try:
        dish = db.dishes.find_one({"_id": ObjectId(dish_id)})
    except Exception:
        pass

    if not dish:
        dish = db.dishes.find_one({"_id": dish_id})

    if not dish:
        raise NotFoundException(name="Dish not found")

    return dish


def _get_restaurant_meta(restaurant_id) -> Tuple[str, str]:
    if not restaurant_id:
        return None, "Restaurant"

    restaurant = None
    try:
        restaurant = db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except Exception:
        pass

    if not restaurant:
        restaurant = db.restaurants.find_one({"_id": restaurant_id})

    if not restaurant:
        return str(restaurant_id), "Restaurant"

    rid = str(restaurant.get("_id", restaurant_id))
    return rid, restaurant.get("name", "Restaurant")


def _get_or_create_cart(user_id: str) -> Dict:
    cart = db.carts.find_one({"user_id": user_id})
    if cart:
        return cart
    doc = {
        "user_id": user_id,
        "items": [],
        "subtotal": 0.0,
        "updated_at": datetime.utcnow(),
    }
    res = db.carts.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def get_cart(user_id: str) -> Dict:
    cart = _get_or_create_cart(user_id)
    return _serialize_cart(cart)


def add_item(user_id: str, dish_id: str, quantity: int = 1) -> Dict:
    if quantity < 1:
        raise BadRequestException(message="Quantity must be at least 1")

    dish = _fetch_dish(dish_id)
    if not dish:
        raise NotFoundException(name="Dish not found")

    dish_restaurant_id = dish.get("restaurant_id")
    restaurant_id, restaurant_name = _get_restaurant_meta(dish_restaurant_id)
    dish_id_str = str(dish.get("_id", dish_id))

    cart = _get_or_create_cart(user_id)
    items: List[Dict] = cart.get("items", [])
    existing = next((item for item in items if str(item["dish_id"]) == dish_id_str), None)

    if existing:
        existing["quantity"] += quantity
        existing.setdefault("restaurant_id", restaurant_id)
        existing.setdefault("restaurant_name", restaurant_name)
    else:
        items.append(
            {
                "dish_id": dish_id_str,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "name": dish.get("name"),
                "price": dish.get("price", 0.0),
                "quantity": quantity,
                "description": dish.get("description"),
                "ingredients": dish.get("ingredients", []),
                "explicit_allergens": dish.get("explicit_allergens", []),
                "nutrition_facts": dish.get("nutrition_facts", {}),
            }
        )

    cart["items"] = items
    _recalculate(cart)

    db.carts.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": cart["items"], "subtotal": cart["subtotal"], "updated_at": cart["updated_at"]}},
    )
    return _serialize_cart(cart)


def update_item_quantity(user_id: str, dish_id: str, quantity: int) -> Dict:
    if quantity < 1:
        return remove_item(user_id, dish_id)

    cart = _get_or_create_cart(user_id)
    updated = False
    for item in cart.get("items", []):
        if item["dish_id"] == dish_id:
            item["quantity"] = quantity
            updated = True
            break

    if not updated:
        raise NotFoundException(name="Item not found in cart")

    _recalculate(cart)
    db.carts.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": cart["items"], "subtotal": cart["subtotal"], "updated_at": cart["updated_at"]}},
    )
    return _serialize_cart(cart)


def remove_item(user_id: str, dish_id: str) -> Dict:
    cart = _get_or_create_cart(user_id)
    items = [item for item in cart.get("items", []) if item["dish_id"] != dish_id]
    if len(items) == len(cart.get("items", [])):
        raise NotFoundException(name="Item not found in cart")

    cart["items"] = items
    _recalculate(cart)
    db.carts.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": cart["items"], "subtotal": cart["subtotal"], "updated_at": cart["updated_at"]}},
    )
    return _serialize_cart(cart)


def clear_cart(user_id: str) -> Dict:
    cart = _get_or_create_cart(user_id)
    cart["items"] = []
    _recalculate(cart)
    db.carts.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": [], "subtotal": 0.0, "updated_at": cart["updated_at"]}},
    )
    cart["subtotal"] = 0.0
    return _serialize_cart(cart)
