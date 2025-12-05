"""Administrative analytics helpers for SafeBites."""
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
from bson import ObjectId
from app.db import db


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _date_key(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        return value[:10]
    return datetime.utcnow().date().isoformat()


def _fetch_users(user_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Return user documents keyed by their string id."""
    object_ids: List[ObjectId] = []
    seen: set[str] = set()
    for uid in user_ids:
        if not uid or uid in seen:
            continue
        try:
            object_ids.append(ObjectId(uid))
            seen.add(uid)
        except Exception:
            continue
    if not object_ids:
        return {}
    docs = db.users.find({"_id": {"$in": object_ids}})
    return {str(doc["_id"]): doc for doc in docs}


def _format_top_customers(
    user_stats: Dict[str, Dict[str, Any]],
    user_docs: Dict[str, Dict[str, Any]],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Return a list of the highest value customers."""
    sorted_stats = sorted(
        user_stats.items(),
        key=lambda item: item[1]["spend"],
        reverse=True,
    )[:limit]
    top_customers: List[Dict[str, Any]] = []
    for uid, stats in sorted_stats:
        user_doc = user_docs.get(uid, {})
        top_customers.append(
            {
                "user_id": uid,
                "name": user_doc.get("name", "Customer"),
                "orders": stats["orders"],
                "lifetime_value": round(stats["spend"], 2),
                "last_order": stats["last_order"],
                "allergen_preferences": user_doc.get("allergen_preferences", []),
            }
        )
    return top_customers


def _build_allergen_watchlist(
    orders: List[Dict[str, Any]],
    user_docs: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, int], int, int]:
    """Summarize allergen counts and flag risky orders."""
    allergen_counts: Dict[str, int] = {}
    flagged_orders: set[str] = set()
    impacted_users: set[str] = set()

    for order in orders:
        order_id = str(order.get("_id", order.get("id", "")))
        user_id = str(order.get("user_id") or "")
        preferences = {str(p).strip().lower() for p in (user_docs.get(user_id, {}).get("allergen_preferences") or []) if p}
        for item in order.get("items", []) or []:
            qty = int(item.get("quantity", 0) or 0)
            allergens = {str(a).strip().lower() for a in (item.get("explicit_allergens") or []) if a}
            for allergen in allergens:
                allergen_counts[allergen] = allergen_counts.get(allergen, 0) + qty
            if preferences and allergens.intersection(preferences):
                if order_id:
                    flagged_orders.add(order_id)
                if user_id:
                    impacted_users.add(user_id)
    return allergen_counts, len(flagged_orders), len(impacted_users)


def get_platform_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    restaurant_id: Optional[str] = None,
) -> Dict[str, Any]:
    filters: List[Dict[str, Any]] = []
    if start_date or end_date:
        date_query: Dict[str, Any] = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date
        if date_query:
            filters.append({"placed_at": date_query})
    if restaurant_id:
        filters.append(
            {
                "$or": [
                    {"restaurants.restaurant_id": restaurant_id},
                    {"restaurants.restaurant_name": restaurant_id},
                ]
            }
        )

    query: Dict[str, Any]
    if not filters:
        query = {}
    elif len(filters) == 1:
        query = filters[0]
    else:
        query = {"$and": filters}

    orders: List[Dict] = list(db.orders.find(query))

    def _matches_restaurant(entry_id: Optional[str], entry_name: Optional[str]) -> bool:
        if not restaurant_id:
            return True
        if entry_id and str(entry_id) == restaurant_id:
            return True
        if entry_name and entry_name == restaurant_id:
            return True
        return False
    total_orders = len(orders)
    total_revenue = 0.0
    unique_customers = len({o.get("user_id") for o in orders if o.get("user_id")})

    restaurants_map: Dict[str, Dict[str, Any]] = {}
    dish_map: Dict[str, Dict[str, Any]] = {}
    daily_map: Dict[str, Dict[str, Any]] = {}
    user_stats: Dict[str, Dict[str, Any]] = {}
    total_items_sold = 0
    allergen_free_items = 0

    for order in orders:
        day_key = _date_key(order.get("placed_at"))
        daily_entry = daily_map.setdefault(day_key, {"date": day_key, "orders": 0, "revenue": 0.0})
        if restaurant_id:
            order_value = 0.0
            for summary in order.get("restaurants", []) or []:
                if _matches_restaurant(summary.get("restaurant_id"), summary.get("restaurant_name")):
                    order_value = round(order_value + _safe_float(summary.get("item_total")), 2)
            if order_value == 0.0:
                continue
        else:
            order_value = _safe_float(order.get("total"))
        daily_entry["orders"] += 1
        daily_entry["revenue"] = round(daily_entry["revenue"] + order_value, 2)
        total_revenue = round(total_revenue + order_value, 2)

        user_id = str(order.get("user_id") or "")
        if user_id:
            stats = user_stats.setdefault(user_id, {"orders": 0, "spend": 0.0, "last_order": None})
            stats["orders"] += 1
            stats["spend"] = round(stats["spend"] + _safe_float(order.get("total")), 2)
            placed_at = order.get("placed_at")
            if isinstance(placed_at, datetime):
                iso_time = placed_at.isoformat()
            elif isinstance(placed_at, str):
                iso_time = placed_at
            else:
                iso_time = None
            stats["last_order"] = (
                max(filter(None, [stats.get("last_order"), iso_time]))
                if stats.get("last_order") and iso_time
                else iso_time or stats.get("last_order")
            )

        for summary in order.get("restaurants", []) or []:
            if not _matches_restaurant(summary.get("restaurant_id"), summary.get("restaurant_name")):
                continue
            key = summary.get("restaurant_id") or summary.get("restaurant_name") or "unknown"
            entry = restaurants_map.setdefault(
                key,
                {
                    "restaurant_id": summary.get("restaurant_id"),
                    "restaurant_name": summary.get("restaurant_name", "Restaurant"),
                    "order_count": 0,
                    "items_sold": 0,
                    "revenue": 0.0,
                },
            )
            entry["order_count"] += 1
            entry["items_sold"] += int(summary.get("item_count", 0) or 0)
            entry["revenue"] = round(entry["revenue"] + _safe_float(summary.get("item_total")), 2)

        for item in order.get("items", []) or []:
            if not _matches_restaurant(item.get("restaurant_id"), item.get("restaurant_name")):
                continue
            key = item.get("dish_id") or item.get("name")
            entry = dish_map.setdefault(
                key,
                {
                    "dish_id": item.get("dish_id"),
                    "name": item.get("name", "Dish"),
                    "restaurant_name": item.get("restaurant_name", "Restaurant"),
                    "quantity": 0,
                    "revenue": 0.0,
                },
            )
            qty = int(item.get("quantity", 0) or 0)
            entry["quantity"] += qty
            entry["revenue"] = round(entry["revenue"] + (_safe_float(item.get("price")) * qty), 2)
            total_items_sold += qty
            if not (item.get("explicit_allergens") or []):
                allergen_free_items += qty

    restaurants = sorted(restaurants_map.values(), key=lambda r: r["revenue"], reverse=True)
    top_dishes = sorted(dish_map.values(), key=lambda d: d["quantity"], reverse=True)[:5]
    slow_movers = sorted((d for d in dish_map.values() if d["quantity"] > 0), key=lambda d: d["quantity"])[:5]
    daily = sorted(daily_map.values(), key=lambda d: d["date"])[:14]

    totals = {
        "orders": total_orders,
        "revenue": total_revenue,
        "customers": unique_customers,
        "restaurants": len(restaurants),
    }

    user_docs = _fetch_users(list(user_stats.keys()))
    allergen_counts, flagged_orders, impacted_customers = _build_allergen_watchlist(orders, user_docs)
    top_allergens = sorted(allergen_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]

    repeat_customers = sum(1 for stats in user_stats.values() if stats["orders"] > 1)
    new_customers = sum(1 for stats in user_stats.values() if stats["orders"] == 1)
    filtered_customers = len(user_stats) if restaurant_id else unique_customers
    avg_orders_per_customer = (
        round(total_orders / filtered_customers, 2) if filtered_customers else 0.0
    )
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders else 0.0
    avg_items_per_order = round(total_items_sold / total_orders, 2) if total_orders else 0.0
    allergen_free_rate = round((allergen_free_items / total_items_sold) * 100, 2) if total_items_sold else 0.0

    customer_health = {
        "repeat_customers": repeat_customers,
        "new_customers": new_customers,
        "avg_orders_per_customer": avg_orders_per_customer,
        "avg_order_value": avg_order_value,
        "top_customers": _format_top_customers(user_stats, user_docs),
        "allergen_watchlist": {
            "flagged_orders": flagged_orders,
            "impacted_customers": impacted_customers,
            "top_allergens": [
                {"name": name, "count": count}
                for name, count in top_allergens
            ],
        },
    }

    menu_performance = {
        "best_sellers": top_dishes,
        "slow_movers": slow_movers,
        "stats": {
            "unique_dishes": len(dish_map),
            "total_items_sold": total_items_sold,
            "avg_items_per_order": avg_items_per_order,
            "allergen_free_rate": allergen_free_rate,
        },
    }

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "totals": totals,
        "orders_per_day": daily,
        "restaurants": restaurants,
        "top_dishes": top_dishes,
        "customer_health": customer_health,
        "menu_performance": menu_performance,
    }
