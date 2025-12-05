"""Order placement and history services."""
from datetime import datetime, timedelta
from typing import Dict, List
from bson.objectid import ObjectId
from app.db import db
from app.models.exception_model import BadRequestException, NotFoundException
from app.models.order_model import CheckoutRequest


def _serialize_order(order: Dict) -> Dict:
    doc = dict(order)
    doc["_id"] = str(doc["_id"])
    if "placed_at" in doc and isinstance(doc["placed_at"], datetime):
        doc["placed_at"] = doc["placed_at"].isoformat()
    if "estimated_arrival_time" in doc and isinstance(doc["estimated_arrival_time"], datetime):
        doc["estimated_arrival_time"] = doc["estimated_arrival_time"].isoformat()
    return doc


def _summarize_restaurants(items: List[Dict]) -> List[Dict]:
    groups: Dict[str, Dict] = {}
    for item in items or []:
        rid = item.get("restaurant_id")
        rname = item.get("restaurant_name", "Restaurant")
        key = rid or rname
        group = groups.setdefault(
            key,
            {
                "restaurant_id": rid,
                "restaurant_name": rname,
                "item_count": 0,
                "item_total": 0.0,
            },
        )
        qty = item.get("quantity", 0)
        group["item_count"] += qty
        group["item_total"] = round(
            group["item_total"] + (item.get("price", 0.0) * qty),
            2,
        )
    return list(groups.values())


def list_orders(user_id: str) -> List[Dict]:
    orders = list(db.orders.find({"user_id": user_id}).sort("placed_at", -1))
    return [_serialize_order(order) for order in orders]


def get_order(user_id: str, order_id: str) -> Dict:
    try:
        obj_id = ObjectId(order_id)
    except Exception as exc:
        raise NotFoundException(name="Order not found") from exc

    order = db.orders.find_one({"_id": obj_id, "user_id": user_id})
    if not order:
        raise NotFoundException(name="Order not found")
    return _serialize_order(order)


def checkout(user_id: str, payload: CheckoutRequest) -> Dict:
    cart = db.carts.find_one({"user_id": user_id})
    if not cart or not cart.get("items"):
        raise BadRequestException(message="Cart is empty")

    subtotal = round(cart.get("subtotal", 0.0), 2)
    tax = round(subtotal * 0.08, 2)
    fees = 2.50 if subtotal else 0.0
    total = round(subtotal + tax + fees, 2)

    items = cart.get("items", [])
    restaurants = _summarize_restaurants(items)

    now = datetime.utcnow()
    # Estimate arrival dynamically: base prep + per-restaurant and per-item buffers
    restaurant_count = max(len(restaurants), 1)
    total_items = sum(item.get("quantity", 0) or 0 for item in items)
    base_minutes = 35
    restaurant_buffer = max(0, restaurant_count - 1) * 7
    item_buffer = max(0, total_items - 3) * 2
    prep_minutes = min(90, base_minutes + restaurant_buffer + item_buffer)
    arrival_time = now + timedelta(minutes=prep_minutes)

    order_doc = {
        "user_id": user_id,
        "items": items,
        "restaurants": restaurants,
        "subtotal": subtotal,
        "tax": tax,
        "fees": fees,
        "total": total,
        "status": "placed",
        "payment_method": payload.payment_method,
        "delivery_address": payload.delivery_address,
        "special_instructions": payload.special_instructions,
        "placed_at": now,
        "estimated_arrival_time": arrival_time
    }

    res = db.orders.insert_one(order_doc)
    order_doc["_id"] = res.inserted_id

    db.carts.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": [], "subtotal": 0.0, "updated_at": datetime.utcnow()}},
    )

    return _serialize_order(order_doc)
