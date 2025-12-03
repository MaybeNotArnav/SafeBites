"""Order placement and history endpoints."""
from typing import List
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.order_model import CheckoutRequest, OrderOut
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(payload: CheckoutRequest, current_user=Depends(get_current_user)):
    return order_service.checkout(current_user["_id"], payload)


@router.get("/", response_model=List[OrderOut])
def list_orders(current_user=Depends(get_current_user)):
    return order_service.list_orders(current_user["_id"])


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, current_user=Depends(get_current_user)):
    return order_service.get_order(current_user["_id"], order_id)
