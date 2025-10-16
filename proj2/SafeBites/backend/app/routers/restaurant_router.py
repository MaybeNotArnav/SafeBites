from fastapi import APIRouter,HTTPException, Depends
from bson import ObjectId
from app.models.restaurant_model import RestaurantCreate, RestaurantUpdate, RestaurantBase, RestaurantInDB
from app.services import restaurant_service
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from ..services.orchestrator_service import agents
from ..services.intent_service import extract_query_intent
from ..flow.graph import create_chat_graph
from ..flow.state import ChatState
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/",response_model=RestaurantInDB)
def create_restaurant(restaurant: RestaurantCreate):
    """
        Create a new restaurant entry in the database. If allergen information is not provided, 
        it will be inferred using an external service.

        Args:
            restaurant(RestaurantCreate): The restaurant data provided by the client.
        
        Returns:
            RestaurantInDB: The created restaurant entry with its unique ID.
    """
    return restaurant_service.create_restaurant(restaurant)

@router.get("/",response_model=list[RestaurantInDB])
async def list_restaurants():
    """
        Retrieve a list of all restaurants in the database.
        Args:
            None
        
        Returns:
            list[RestaurantInDB]: A list of all restaurant entries in the database.
    """
    return await restaurant_service.get_restaurants()

class ChatQuery(BaseModel):
    query: str
    restaurant_id: Optional[str] = None

@router.post("/search")
async def chat_search(payload: ChatQuery):
    """
    Endpoint to handle user menu queries using the multi-agent pipeline.
    Returns a structured JSON suitable for frontend rendering.
    """
    try:
        chat_graph = create_chat_graph()
        query = "Any pizza under $20 that includes pepperoni?"
        state = ChatState(user_id="u123", session_id="sess001",restaurant_id="rest_1", query=query,query_parts={})
        
        final_state = chat_graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{restaurant_id}",response_model=RestaurantInDB)
def get_restaurant(restaurant_id:str):
    """
        Retrieve a specific restaurant by its ID.

        Args:
            restaurant_id(str): The unique identifier of the restaurant.
        
        Returns:
            RestaurantInDB: The restaurant entry corresponding to the provided ID.
        
        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restaurant_service.get_restaurant_by_id(restaurant_id)

@router.patch("/{restaurant_id}",response_model=RestaurantInDB)
def update_restaurant(restaurant_id:str,updates:RestaurantUpdate):
    """
        Update an existing restaurant's information.

        Args:
            restaurant_id(str): The unique identifier of the restaurant to be updated.
            updates(RestaurantUpdate): The fields to be updated with their new values.

        Returns:
            RestaurantInDB: The updated restaurant entry.
        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restaurant_service.update_restaurant(restaurant_id,updates)

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id:str):
    """
        Delete a restaurant from the database.

        Args:
            restaurant_id(str): The unique identifier of the restaurant to be deleted.

        Returns:
            None

        Raises:
            HTTPException(404): If no restaurant with the given ID is found.
    """
    return restaurant_service.delete_restaurant(restaurant_id)