from fastapi import APIRouter, Header, Depends
from typing import Optional
from app.models.user_model import UserCreate, UserUpdate, UserOut
from app.services import user_service
from app.models.exception_model import AuthError, BadRequestException


router = APIRouter(prefix="/users", tags=["users"])

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise AuthError(detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError(detail="Invalid auth header")
    return user_service.get_user_by_id(token)

@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate):
    return user_service.create_user(payload)

@router.post("/login")
def login(username: str, password: str):
    # uses query params: POST /users/login?username=alice&password=secret
    return user_service.login_user(username, password)

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, current_user=Depends(get_current_user)):
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return user_service.update_user(current_user["_id"], data)

@router.delete("/me")
def delete_me(current_user=Depends(get_current_user)):
    user_service.delete_user(current_user["_id"])
    return {"detail": "deleted"}

@router.get("/{id_or_username}", response_model=UserOut)
def get_user(id_or_username: str):
    # try id first, else username
    try:
        return user_service.get_user_by_id(id_or_username)
    except Exception:
        return user_service.get_user_by_username(id_or_username)
