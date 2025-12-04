"""
Router for reviews endpoints.
"""
from fastapi import APIRouter, Depends
from app.models.review_model import ReviewCreate, ReviewUpdate
from app.services.review_service import (
    create_review as svc_create_review,
    list_reviews_by_dish as svc_list_reviews_by_dish,
    list_reviews_by_user as svc_list_reviews_by_user,
    update_review as svc_update_review,
    delete_review as svc_delete_review,
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"]) 


@router.post("/", status_code=201)
def create_review(payload: ReviewCreate, current_user=Depends(get_current_user)):
    return svc_create_review(current_user["_id"], payload)


@router.get("/dish/{dish_id}")
def list_reviews_for_dish(dish_id: str):
    return svc_list_reviews_by_dish(dish_id)


@router.get("/me")
def list_my_reviews(current_user=Depends(get_current_user)):
    return svc_list_reviews_by_user(current_user["_id"])


@router.patch("/{review_id}")
def update_review(review_id: str, payload: ReviewUpdate, current_user=Depends(get_current_user)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return svc_update_review(review_id, current_user["_id"], data)


@router.delete("/{review_id}")
def delete_review(review_id: str, current_user=Depends(get_current_user)):
    return svc_delete_review(review_id, current_user["_id"])
