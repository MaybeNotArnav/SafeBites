"""Shared authentication dependencies for FastAPI routers."""
from typing import Optional
from fastapi import Header, Depends
from app.models.exception_model import AuthError
from app.services import user_service


def get_current_user(authorization: Optional[str] = Header(None)):
    """Validate Bearer token and return the current user document."""
    if not authorization:
        raise AuthError(detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError(detail="Invalid auth header")
    return user_service.get_user_by_id(token)


def require_admin_user(current_user=Depends(get_current_user)):
    """Ensure the current user has admin privileges."""
    if current_user.get("role") != "admin":
        raise AuthError(detail="Admin access required")
    return current_user
