# backend/app/services/user_service.py
from ..db import db
from bson import ObjectId
from app.models.exception_model import ResourceNotFound, ConflictError, AuthError, BadRequest, DatabaseException
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _strip_password(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc["_id"])
    doc.pop("password", None)
    return doc

async def create_user(user_create):
    # enforce unique username
    existing = await db.users.find_one({"username": user_create.username})
    if existing:
        raise ConflictError(detail="Username already taken")

    hashed = pwd_ctx.hash(user_create.password)
    doc = user_create.model_dump()
    doc["password"] = hashed
    try:
        res = await db.users.insert_one(doc)
        created = await db.users.find_one({"_id": res.inserted_id})
        return _strip_password(created)
    except Exception as e:
        raise DatabaseException(message=f"Failed to create user: {e}")

async def login_user(username: str, password: str):
    user = await db.users.find_one({"username": username})
    if not user or not pwd_ctx.verify(password, user.get("password", "")):
        raise AuthError(detail="Invalid username or password")
    return {"access_token": str(user["_id"]), "token_type": "bearer"}

async def get_user_by_id(user_id: str):
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid user id")
    user = await db.users.find_one({"_id": obj})
    if not user:
        raise ResourceNotFound(detail="User not found")
    return _strip_password(user)

async def get_user_by_username(username: str):
    user = await db.users.find_one({"username": username})
    if not user:
        raise ResourceNotFound(detail="User not found")
    return _strip_password(user)

async def update_user(user_id: str, update_data: dict):
    if not update_data:
        raise BadRequest(detail="No fields to update")
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid user id")
    await db.users.update_one({"_id": obj}, {"$set": update_data})
    updated = await db.users.find_one({"_id": obj})
    return _strip_password(updated)

async def delete_user(user_id: str):
    try:
        obj = ObjectId(user_id)
    except Exception:
        raise ResourceNotFound(detail="Invalid user id")
    res = await db.users.delete_one({"_id": obj})
    if res.deleted_count == 0:
        raise ResourceNotFound(detail="User not found")
    return
