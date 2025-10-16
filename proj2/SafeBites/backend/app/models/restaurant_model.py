from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RestaurantBase(BaseModel):
    name:str
    location:str
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantCreate(RestaurantBase):
    name:str
    location:str
    cuisine:Optional[List[str]]
    rating:Optional[float] = Field(default=0.0,ge=0,le=5.0)

class RestaurantUpdate(BaseModel):
    name:Optional[str] = None
    location:Optional[str] = None
    cuisine:Optional[List[str]] = None
    rating:Optional[float] = None

class RestaurantInDB(RestaurantBase):
    id:str = Field(alias="_id")

    class Config:
        populate_by_name = True