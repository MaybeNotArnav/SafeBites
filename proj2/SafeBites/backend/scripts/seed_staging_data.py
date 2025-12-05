"""Populate staging data with diverse allergens, dishes, and restaurants.

This script inserts sample users, restaurants, dishes, and orders so that the
admin analytics dashboard has realistic data to aggregate. Orders include
explicit allergen metadata to exercise the allergen watchlist.
"""
from __future__ import annotations

import argparse
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from bson import ObjectId
from dotenv import load_dotenv
from passlib.context import CryptContext
from pymongo import MongoClient

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "foodapp_test")
SEED_TAG = "staging-demo"

if not MONGO_URI:
    raise RuntimeError("MONGO_URI must be set in backend/.env before running the seeder")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

SAMPLE_USERS = [
    {
        "name": "Avery Patel",
        "username": "avery",
        "password": "demo123",
        "allergen_preferences": ["peanuts", "shellfish"],
        "role": "user",
    },
    {
        "name": "Jordan Smith",
        "username": "jordan",
        "password": "demo123",
        "allergen_preferences": ["dairy"],
        "role": "user",
    },
    {
        "name": "Morgan Yu",
        "username": "morgan",
        "password": "demo123",
        "allergen_preferences": ["sesame", "soy"],
        "role": "user",
    },
    {
        "name": "Admin Scout",
        "username": "admin_scout",
        "password": "demo123",
        "allergen_preferences": [],
        "role": "admin",
    },
]

SAMPLE_RESTAURANTS = [
    {
        "_id": "rest_stage_italian",
        "name": "Crimson Pasta House",
        "location": "Raleigh, NC",
        "cuisine": ["Italian"],
        "rating": 4.6,
    },
    {
        "_id": "rest_stage_mexican",
        "name": "Sol y Sabor Taqueria",
        "location": "Durham, NC",
        "cuisine": ["Mexican"],
        "rating": 4.4,
    },
    {
        "_id": "rest_stage_asian",
        "name": "Lotus & Fire",
        "location": "Cary, NC",
        "cuisine": ["Pan-Asian"],
        "rating": 4.7,
    },
]

SAMPLE_DISHES = [
    {
        "_id": "dish_stage_lasagna",
        "restaurant_id": "rest_stage_italian",
        "name": "Truffle Spinach Lasagna",
        "description": "Layers of pasta with ricotta, spinach, and truffle cream sauce.",
        "price": 19.5,
        "ingredients": ["pasta", "ricotta", "spinach", "cream", "truffle oil"],
        "explicit_allergens": ["dairy", "wheat_gluten"],
    },
    {
        "_id": "dish_stage_bruschetta",
        "restaurant_id": "rest_stage_italian",
        "name": "Heirloom Tomato Bruschetta",
        "description": "Toasted baguette topped with basil pesto and tomatoes.",
        "price": 11.0,
        "ingredients": ["bread", "basil", "parmesan", "tomato"],
        "explicit_allergens": ["dairy", "wheat_gluten"],
    },
    {
        "_id": "dish_stage_taco",
        "restaurant_id": "rest_stage_mexican",
        "name": "Ancho-Lime Shrimp Taco",
        "description": "Shrimp taco with pickled red cabbage and chipotle crema.",
        "price": 6.5,
        "ingredients": ["shrimp", "corn tortilla", "cabbage", "chipotle crema"],
        "explicit_allergens": ["shellfish", "dairy"],
    },
    {
        "_id": "dish_stage_carnitas",
        "restaurant_id": "rest_stage_mexican",
        "name": "Citrus Carnitas Bowl",
        "description": "Slow-braised pork with citrus glaze, beans, and rice.",
        "price": 14.25,
        "ingredients": ["pork", "beans", "rice", "citrus"],
        "explicit_allergens": [],
    },
    {
        "_id": "dish_stage_ramen",
        "restaurant_id": "rest_stage_asian",
        "name": "Black Garlic Tonkatsu Ramen",
        "description": "Pork broth ramen with soft egg and sesame chili oil.",
        "price": 17.0,
        "ingredients": ["pork broth", "noodles", "egg", "sesame oil"],
        "explicit_allergens": ["egg", "sesame", "wheat_gluten"],
    },
    {
        "_id": "dish_stage_bowl",
        "restaurant_id": "rest_stage_asian",
        "name": "Crispy Tofu Power Bowl",
        "description": "Sesame-crusted tofu with quinoa, edamame, and citrus dressing.",
        "price": 15.75,
        "ingredients": ["tofu", "sesame", "quinoa", "edamame"],
        "explicit_allergens": ["soy", "sesame"],
    },
]


def upsert_users() -> Dict[str, str]:
    """Insert or update sample users and return username -> user_id map."""
    user_ids: Dict[str, str] = {}
    for user in SAMPLE_USERS:
        existing = db.users.find_one({"username": user["username"]})
        if existing:
            user_ids[user["username"]] = str(existing["_id"])
            db.users.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "name": user["name"],
                        "allergen_preferences": user["allergen_preferences"],
                        "role": user["role"],
                        "metadata.seed_tag": SEED_TAG,
                    }
                },
            )
            continue
        hashed = pwd_ctx.hash(user["password"])  # simple demo password
        doc = {
            "name": user["name"],
            "username": user["username"],
            "password": hashed,
            "allergen_preferences": user["allergen_preferences"],
            "role": user["role"],
            "created_at": datetime.utcnow(),
            "metadata": {"seed_tag": SEED_TAG},
        }
        res = db.users.insert_one(doc)
        user_ids[user["username"]] = str(res.inserted_id)
    return user_ids


def upsert_restaurants() -> Dict[str, Dict]:
    """Ensure sample restaurants exist and return map keyed by id."""
    for rest in SAMPLE_RESTAURANTS:
        rest.setdefault("metadata", {})
        rest["metadata"]["seed_tag"] = SEED_TAG
        db.restaurants.update_one({"_id": rest["_id"]}, {"$set": rest}, upsert=True)
    docs = list(db.restaurants.find({"_id": {"$in": [r["_id"] for r in SAMPLE_RESTAURANTS]}}))
    return {doc["_id"]: doc for doc in docs}


def upsert_dishes(restaurants: Dict[str, Dict]) -> Dict[str, Dict]:
    """Insert dishes tied to the seed restaurants."""
    for dish in SAMPLE_DISHES:
        rest_name = restaurants[dish["restaurant_id"]]["name"]
        enriched = {
            **dish,
            "restaurant_name": rest_name,
            "ingredients": dish["ingredients"],
            "nutrition_facts": {
                "calories": {"value": random.randint(400, 750)},
                "protein": {"value": random.randint(15, 35)},
                "fat": {"value": random.randint(10, 30)},
                "carbohydrates": {"value": random.randint(30, 80)},
            },
            "metadata": {"seed_tag": SEED_TAG},
        }
        db.dishes.update_one({"_id": dish["_id"]}, {"$set": enriched}, upsert=True)
    docs = list(db.dishes.find({"_id": {"$in": [d["_id"] for d in SAMPLE_DISHES]}}))
    return {doc["_id"]: doc for doc in docs}


def _summarize_restaurants(items: List[Dict]) -> List[Dict]:
    groups: Dict[str, Dict] = {}
    for item in items:
        rid = item.get("restaurant_id")
        key = rid or item.get("restaurant_name")
        group = groups.setdefault(
            key,
            {
                "restaurant_id": rid,
                "restaurant_name": item.get("restaurant_name"),
                "item_count": 0,
                "item_total": 0.0,
            },
        )
        qty = item.get("quantity", 0)
        group["item_count"] += qty
        group["item_total"] = round(group["item_total"] + (item.get("price", 0.0) * qty), 2)
    return list(groups.values())


def build_order_items(selected: List[Tuple[Dict, int]]) -> List[Dict]:
    items: List[Dict] = []
    for dish, qty in selected:
        items.append(
            {
                "dish_id": dish["_id"],
                "restaurant_id": dish["restaurant_id"],
                "restaurant_name": dish.get("restaurant_name"),
                "name": dish["name"],
                "price": dish["price"],
                "quantity": qty,
                "description": dish.get("description"),
                "ingredients": dish.get("ingredients", []),
                "explicit_allergens": dish.get("explicit_allergens", []),
                "nutrition_facts": dish.get("nutrition_facts", {}),
            }
        )
    return items


def seed_orders(
    user_ids: Dict[str, str],
    dishes: Dict[str, Dict],
    order_count: int,
    days: int,
    reset: bool,
) -> None:
    if reset:
        db.orders.delete_many({"metadata.seed_tag": SEED_TAG})

    dish_list = list(dishes.values())
    usernames = list(user_ids.keys())
    now = datetime.utcnow()

    bulk_orders: List[Dict] = []
    for idx in range(order_count):
        user_key = random.choice(usernames)
        user_id = user_ids[user_key]
        placed_at = now - timedelta(days=random.randint(0, days), hours=random.randint(0, 23))
        selected_count = random.randint(1, 3)
        chosen = random.sample(dish_list, selected_count)
        items_with_qty = [(dish, random.randint(1, 3)) for dish in chosen]
        items = build_order_items(items_with_qty)
        subtotal = round(sum(item["price"] * item["quantity"] for item in items), 2)
        tax = round(subtotal * 0.08, 2)
        fees = 2.5 if subtotal else 0.0
        total = round(subtotal + tax + fees, 2)
        order_doc = {
            "user_id": user_id,
            "items": items,
            "restaurants": _summarize_restaurants(items),
            "subtotal": subtotal,
            "tax": tax,
            "fees": fees,
            "total": total,
            "status": random.choice(["placed", "completed", "completed", "cancelled"]),
            "payment_method": "card",
            "delivery_address": "123 Demo St",
            "special_instructions": random.choice([
                "",
                "extra napkins",
                "light on salt",
                "allergy noted",
            ]),
            "placed_at": placed_at,
            "metadata": {"seed_tag": SEED_TAG},
        }
        bulk_orders.append(order_doc)

    if bulk_orders:
        db.orders.insert_many(bulk_orders)



def main() -> None:
    parser = argparse.ArgumentParser(description="Seed staging data for analytics dashboards")
    parser.add_argument("--orders", type=int, default=60, help="Number of sample orders to create")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Spread orders across the last N days",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove previously seeded demo docs before inserting new ones",
    )
    args = parser.parse_args()

    user_ids = upsert_users()
    restaurants = upsert_restaurants()
    dishes = upsert_dishes(restaurants)
    seed_orders(user_ids, dishes, order_count=args.orders, days=args.days, reset=args.reset)
    print(
        f"Seeded {args.orders} staged orders across {len(restaurants)} restaurants with tag '{SEED_TAG}'."
    )


if __name__ == "__main__":
    main()
