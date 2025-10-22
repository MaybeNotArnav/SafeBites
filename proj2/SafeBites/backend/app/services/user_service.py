from ..db import db
from bson import ObjectId
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _strip_password(doc):
    doc["_id"] = str(doc["_id"])
    doc.pop("password", None)
    return doc

async def create_user(data):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_ctx.hash(data.password)
    user_doc = data.model_dump()
    user_doc["password"] = hashed_pw

    res = await db.users.insert_one(user_doc)
    new_user = await db.users.find_one({"_id": res.inserted_id})
    return _strip_password(new_user)

async def login_user(email: str, password: str):
    user = await db.users.find_one({"email": email})
    if not user or not pwd_ctx.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": str(user["_id"]), "token_type": "bearer"}

async def get_user_by_id(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _strip_password(user)

async def update_user(user_id: str, update_data: dict):
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
    updated = await db.users.find_one({"_id": ObjectId(user_id)})
    return _strip_password(updated)

async def delete_user(user_id: str):
    res = await db.users.delete_one({"_id": ObjectId(user_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
