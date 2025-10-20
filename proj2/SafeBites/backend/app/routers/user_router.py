from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from ..db import db
from ..models.user_model import UserCreate, UserUpdate, UserOut
from passlib.context import CryptContext
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["users"])
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _to_out(doc):
    doc["_id"] = str(doc["_id"])
    doc.pop("password", None)
    return doc

@router.post("/signup")
async def signup(payload: UserCreate):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_ctx.hash(payload.password)
    doc = payload.model_dump()
    doc["password"] = hashed
    res = await db.users.insert_one(doc)
    created = await db.users.find_one({"_id": res.inserted_id})
    return _to_out(created)

@router.post("/login")
async def login(email: str, password: str):
    user = await db.users.find_one({"email": email})
    if not user or not pwd_ctx.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # return a simple user id token (for demo). Replace with JWT in prod.
    return {"access_token": str(user["_id"]), "token_type": "bearer"}

# simple dependency to get user by token (token is user id)
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid auth header")
    user = await db.users.find_one({"_id": ObjectId(token)})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return _to_out(user)

@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, current_user=Depends(get_current_user)):
    update_doc = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_doc:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.users.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": update_doc})
    updated = await db.users.find_one({"_id": ObjectId(current_user["_id"])})
    return _to_out(updated)

@router.delete("/me")
async def delete_me(current_user=Depends(get_current_user)):
    await db.users.delete_one({"_id": ObjectId(current_user["_id"])})
    return {"detail": "deleted"}
