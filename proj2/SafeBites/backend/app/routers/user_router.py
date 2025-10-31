"""
USER ROUTER
APIs implemented:
1. POST   /users/signup          → Create new user
2. POST   /users/login           → Login & get token (username+password)
3. GET    /users/me              → Get logged-in user profile
4. PUT    /users/me              → Update profile
5. DELETE /users/me              → Delete user
6. GET    /users/{id_or_username}→ Get user by ID or username
"""
from fastapi import APIRouter, Header, Depends
from typing import Optional
from ..models.user_model import UserCreate, UserUpdate, UserOut
from ..services import user_service
from app.models.exception_model import AuthError

router = APIRouter(prefix="/users", tags=["users"])

# Dependency to get current user (Bearer token = user_id)
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise AuthError(detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError(detail="Invalid auth header")
    return await user_service.get_user_by_id(token)

@router.post("/signup", response_model=UserOut)
async def signup(payload: UserCreate):
    return await user_service.create_user(payload)

@router.post("/login")
async def login(username: str, password: str):
    return await user_service.login_user(username, password)

@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, current_user=Depends(get_current_user)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return await user_service.update_user(current_user["_id"], data)

@router.delete("/me")
async def delete_me(current_user=Depends(get_current_user)):
    await user_service.delete_user(current_user["_id"])
    return {"detail": "deleted"}

@router.get("/{id_or_username}", response_model=UserOut)
async def get_user(id_or_username: str):
    # try id first, else username
    try:
        return await user_service.get_user_by_id(id_or_username)
    except Exception:
        return await user_service.get_user_by_username(id_or_username)
