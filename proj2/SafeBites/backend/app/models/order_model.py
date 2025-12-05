"""Pydantic schemas for cart and order operations."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, conint


class CartItem(BaseModel):
    dish_id: str
    restaurant_id: Optional[str] = None
    restaurant_name: Optional[str] = None
    name: str
    price: float
    quantity: conint(ge=1) = 1
    description: Optional[str] = None
    ingredients: List[str] = Field(default_factory=list)
    explicit_allergens: List[Any] = Field(default_factory=list)
    nutrition_facts: Optional[Dict[str, Any]] = None


class CartItemAdd(BaseModel):
    dish_id: str
    quantity: conint(ge=1) = 1


class CartItemUpdate(BaseModel):
    quantity: conint(ge=1)


class CartOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    subtotal: float = 0.0
    updated_at: datetime


class CheckoutRequest(BaseModel):
    payment_method: Optional[str] = "card"
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None


class OrderItem(CartItem):
    pass


class RestaurantOrderSummary(BaseModel):
    restaurant_id: Optional[str] = None
    restaurant_name: Optional[str] = None
    item_count: int = 0
    item_total: float = 0.0


class OrderOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    items: List[OrderItem]
    restaurants: List[RestaurantOrderSummary] = Field(default_factory=list)
    subtotal: float
    tax: float
    fees: float
    total: float
    status: str
    payment_method: Optional[str] = None
    delivery_address: Optional[str] = None
    special_instructions: Optional[str] = None
    placed_at: datetime
    estimated_arrival_time: Optional[datetime] = None
