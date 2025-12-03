"""API endpoints for managing user shopping carts."""
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.order_model import CartItemAdd, CartItemUpdate, CartOut
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartOut)
def get_cart(current_user=Depends(get_current_user)):
    return cart_service.get_cart(current_user["_id"])


@router.post("/items", response_model=CartOut, status_code=201)
def add_item(payload: CartItemAdd, current_user=Depends(get_current_user)):
    return cart_service.add_item(current_user["_id"], payload.dish_id, payload.quantity)


@router.patch("/items/{dish_id}", response_model=CartOut)
def update_item(dish_id: str, payload: CartItemUpdate, current_user=Depends(get_current_user)):
    return cart_service.update_item_quantity(current_user["_id"], dish_id, payload.quantity)


@router.delete("/items/{dish_id}", response_model=CartOut)
def remove_item(dish_id: str, current_user=Depends(get_current_user)):
    return cart_service.remove_item(current_user["_id"], dish_id)


@router.post("/clear", response_model=CartOut)
def clear_cart(current_user=Depends(get_current_user)):
    return cart_service.clear_cart(current_user["_id"])
