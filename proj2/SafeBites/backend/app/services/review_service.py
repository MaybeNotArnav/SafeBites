"""
Service layer for managing reviews.

Implements create/list/update/delete and enforces one-review-per-user-per-dish.
"""
from ..db import db
from bson.objectid import ObjectId
from datetime import datetime
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException, ConflictException


def _to_out(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    # normalize ids to strings for output
    doc["user_id"] = str(doc["user_id"]) if isinstance(doc.get("user_id"), ObjectId) else doc.get("user_id")
    doc["dish_id"] = str(doc["dish_id"]) if isinstance(doc.get("dish_id"), ObjectId) else doc.get("dish_id")

    # attach the review author's display name when possible
    try:
        raw_user = doc.get("user_id")
        user_doc = None
        # try ObjectId lookup first
        try:
            user_doc = db.users.find_one({"_id": ObjectId(raw_user)})
        except Exception:
            # fall back to string-based lookup (username or id stored as string)
            user_doc = db.users.find_one({"_id": raw_user}) or db.users.find_one({"username": raw_user})

        if user_doc:
            doc["userName"] = user_doc.get("name") or user_doc.get("username")
        else:
            doc["userName"] = None
    except Exception:
        doc["userName"] = None
    return doc


def _normalize_id(val: str):
    """Try to convert `val` to an ObjectId; if it fails, return the original string.

    This allows the API to accept both MongoDB ObjectId hex strings and
    application-specific string IDs like 'dish_1'.
    """
    if val is None:
        return val
    try:
        return ObjectId(val)
    except Exception:
        return val


def create_review(user_id: str, payload):
    """Create a review, enforcing one review per user per dish."""
    # Accept either ObjectId-style hex strings or custom string IDs
    user_obj = _normalize_id(user_id)
    dish_obj = _normalize_id(payload.dish_id)

    # enforce one per user/dish (works whether ids are ObjectId or plain strings)
    existing = db.reviews.find_one({"user_id": user_obj, "dish_id": dish_obj})
    if existing:
        raise ConflictException(detail="User has already reviewed this dish")

    now = datetime.utcnow().isoformat()
    doc = {
        "user_id": user_obj,
        "dish_id": dish_obj,
        "rating": int(payload.rating),
        "comment": payload.comment,
        "created_at": now,
        "updated_at": now,
    }
    try:
        res = db.reviews.insert_one(doc)
        created = db.reviews.find_one({"_id": res.inserted_id})
        return _to_out(created)
    except Exception as e:
        raise DatabaseException(message=f"Failed to create review: {e}")


def list_reviews_by_dish(dish_id: str):
    dish_obj = _normalize_id(dish_id)
    docs = list(db.reviews.find({"dish_id": dish_obj}).sort("created_at", -1))
    return [_to_out(d) for d in docs]


def list_reviews_by_user(user_id: str):
    user_obj = _normalize_id(user_id)
    docs = list(db.reviews.find({"user_id": user_obj}).sort("created_at", -1))
    return [_to_out(d) for d in docs]


def update_review(review_id: str, user_id: str, update_data: dict):
    try:
        r_obj = ObjectId(review_id)
    except Exception:
        raise NotFoundException(name="Invalid review id")

    existing = db.reviews.find_one({"_id": r_obj})
    if not existing:
        raise NotFoundException(name="Review not found")

    # Compare string forms so it works whether stored id is ObjectId or plain string
    if str(existing.get("user_id")) != str(user_id):
        raise BadRequestException(message="User not authorized to update this review")

    update_data["updated_at"] = datetime.utcnow().isoformat()
    res = db.reviews.update_one({"_id": r_obj}, {"$set": update_data})
    if res.matched_count == 0:
        raise DatabaseException(message="Failed to update review")
    updated = db.reviews.find_one({"_id": r_obj})
    return _to_out(updated)


def delete_review(review_id: str, user_id: str):
    try:
        r_obj = ObjectId(review_id)
    except Exception:
        raise NotFoundException(name="Invalid review id")

    existing = db.reviews.find_one({"_id": r_obj})
    if not existing:
        raise NotFoundException(name="Review not found")

    if str(existing.get("user_id")) != str(user_id):
        raise BadRequestException(message="User not authorized to delete this review")

    res = db.reviews.delete_one({"_id": r_obj})
    if res.deleted_count == 0:
        raise DatabaseException(message="Failed to delete review")
    return {"detail": "deleted"}


def get_review_stats_for_dish(dish_id: str):
    """Return average rating and count for a dish."""
    dish_obj = _normalize_id(dish_id)

    pipeline = [
        {"$match": {"dish_id": dish_obj}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    res = list(db.reviews.aggregate(pipeline))
    if not res:
        return {"avg": None, "count": 0}
    return {"avg": float(res[0].get("avg", 0)), "count": int(res[0].get("count", 0))}
