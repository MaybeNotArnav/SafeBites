"""
Defines API endpoints for user account management and authentication.

Endpoints include:

- POST /users/signup : Register a new user account.
- POST /users/login : Authenticate a user and return a session token.
- GET /users/me : Retrieve the currently authenticated user's profile.
- PUT /users/me : Update the currently authenticated user's profile.
- DELETE /users/me : Delete the currently authenticated user's account.
- GET /users/{id_or_username} : Retrieve a user by ID or username.

Authentication:
- `Authorization: Bearer <token>` header is used for protected routes (`/me` endpoints).
- Auth token is validated using `get_current_user` dependency.
"""
from fastapi import APIRouter, Depends
from app.models.user_model import UserCreate, UserUpdate, UserOut
from app.services import user_service
from app.models.exception_model import BadRequestException
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserOut)
def signup(payload: UserCreate):
    """
    Register a new user.

    Args:
        payload (UserCreate): The user registration data (name, username, password, allergen preferences).

    Returns:
        UserOut: The created user document.
    """
    return user_service.create_user(payload)

@router.post("/login")
def login(username: str, password: str):
    """
    Authenticate a user and return their session token.

    This uses query parameters:
    `POST /users/login?username=<username>&password=<password>`

    Args:
        username (str): The username of the user.
        password (str): The user's password.

    Returns:
        dict: A token or session data for authenticated users.

    Raises:
        AuthError: If authentication fails.
    """
    # uses query params: POST /users/login?username=alice&password=secret
    return user_service.login_user(username, password)

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.

    Args:
        current_user (dict): The user data injected via dependency.

    Returns:
        UserOut: The current user’s profile information.
    """
    return current_user

@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, current_user=Depends(get_current_user)):
    """
    Update the profile of the currently authenticated user.

    Args:
        payload (UserUpdate): Fields to update (e.g., name, allergen preferences).
        current_user (dict): The authenticated user.

    Returns:
        UserOut: The updated user document.
    """
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return user_service.update_user(current_user["_id"], data)

@router.delete("/me")
def delete_me(current_user=Depends(get_current_user)):
    """
    Delete the account of the currently authenticated user.

    Args:
        current_user (dict): The authenticated user.

    Returns:
        dict: A message confirming deletion.
    """
    user_service.delete_user(current_user["_id"])
    return {"detail": "deleted"}

@router.get("/{id_or_username}", response_model=UserOut)
def get_user(id_or_username: str):
    """
    Retrieve a user by either ID or username.

    Args:
        id_or_username (str): The user's ID or username.

    Returns:
        UserOut: The user document if found.

    Raises:
        BadRequestException: If the user is not found by either method.
    """
    # try id first, else username
    try:
        return user_service.get_user_by_id(id_or_username)
    except Exception:
        return user_service.get_user_by_username(id_or_username)
