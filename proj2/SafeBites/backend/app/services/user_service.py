"""
User Management Service

Provides CRUD operations for user accounts, including authentication and password management.
"""
from app.db import db
from bson.objectid import ObjectId
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException, ConflictException
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _strip_password(doc: dict) -> dict:
    """
    Remove sensitive password information from a user document.

    Parameters
    ----------
    doc : dict
        User document retrieved from the database.

    Returns
    -------
    dict
        User document with the "_id" converted to string and "password" removed.
    """
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    doc.pop("password", None)
    return doc

def create_user(user_create):
    """
    Create a new user in the database with hashed password.

    Parameters
    ----------
    user_create : UserCreate
        Pydantic model containing user registration details.

    Returns
    -------
    dict
        Created user document with password removed.

    Raises
    ------
    ConflictException
        If the username is already taken.
    DatabaseException
        If insertion into the database fails.
    """
    # enforce unique username globally
    existing = db.users.find_one({"username": user_create.username})
    if existing:
        raise ConflictException(detail="Username already taken")
    hashed = pwd_ctx.hash(user_create.password[:72])
    doc = user_create.model_dump()
    doc["password"] = hashed
    try:
        res = db.users.insert_one(doc)
        created = db.users.find_one({"_id": res.inserted_id})
        return _strip_password(created)
    except Exception as e:
        raise DatabaseException(message=f"Failed to create user: {e}")

def login_user(username: str, password: str):
    """
    Authenticate a user with username and password.

    Parameters
    ----------
    username : str
        Username of the user.
    password : str
        Plain-text password provided by the user.

    Returns
    -------
    dict
        Access token and token type if authentication succeeds.

    Raises
    ------
    BadRequestException
        If username does not exist or password is incorrect.
    """
    user = db.users.find_one({"username": username})
    if not user or not pwd_ctx.verify(password, user.get("password", "")):
        raise BadRequestException(message="Invalid username or password")
    # demo token: user id
    return {"access_token": str(user["_id"]), "token_type": "bearer"}

def get_user_by_id(user_id: str):
    """
    Retrieve a user by their unique user ID.

    Parameters
    ----------
    user_id : str
        Unique user identifier (MongoDB ObjectId).

    Returns
    -------
    dict
        User document with password removed.

    Raises
    ------
    NotFoundException
        If the user ID is invalid or the user does not exist.
    """
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    user = db.users.find_one({"_id": obj})
    if not user:
        raise NotFoundException(name="User not found")
    return _strip_password(user)

def get_user_by_username(username: str):
    """
    Retrieve a user by their username.

    Parameters
    ----------
    username : str
        Username of the user.

    Returns
    -------
    dict
        User document with password removed.

    Raises
    ------
    NotFoundException
        If the user does not exist.
    """
    user = db.users.find_one({"username": username})
    if not user:
        raise NotFoundException(name="User not found")
    return _strip_password(user)

def update_user(user_id: str, update_data: dict):
    """
    Update an existing user's details.

    Parameters
    ----------
    user_id : str
        Unique user identifier (MongoDB ObjectId).
    update_data : dict
        Fields to update in the user document.

    Returns
    -------
    dict
        Updated user document with password removed.

    Raises
    ------
    BadRequestException
        If no update fields are provided.
    NotFoundException
        If the user ID is invalid or the user does not exist.
    """
    if not update_data:
        raise BadRequestException(message="No fields to update")
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    db.users.update_one({"_id": obj}, {"$set": update_data})
    updated = db.users.find_one({"_id": obj})
    return _strip_password(updated)

def delete_user(user_id: str):
    """
    Delete a user from the database.

    Parameters
    ----------
    user_id : str
        Unique user identifier (MongoDB ObjectId).

    Raises
    ------
    NotFoundException
        If the user ID is invalid or the user does not exist.
    """
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise NotFoundException(name="Invalid user id")
    res = db.users.delete_one({"_id": obj})
    if res.deleted_count == 0:
        raise NotFoundException(name="User not found")
    return
