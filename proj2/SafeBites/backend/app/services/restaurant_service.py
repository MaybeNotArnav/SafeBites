import logging
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.models.exception_model import NotFoundException, BadRequestException, DatabaseException,GenericException
from app.models.restaurant_model import RestaurantCreate, RestaurantUpdate, RestaurantInDB
from app.db import get_db
from pymongo.errors import PyMongoError
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os, json
from dotenv import load_dotenv
from ..utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)

load_dotenv()
db = get_db()

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

restaurant_collection = db["restaurants"]

def create_restaurant(restaurant:RestaurantCreate):
    """
        Creates a new restaurant in the database.

        Args:
            restaurant (RestaurantCreate): The restaurant data to create.
            Example:
            {
                "name": "Pasta Palace",
                "address": "123 Noodle St, Food City",
                "cuisine": "Italian",
                "rating":4.5
            }

        Returns:
            RestaurantInDB: The created restaurant with its ID.
    """
    try:
        result = restaurant_collection.insert_one(restaurant.dict())
        if not result.inserted_id:
            raise BadRequestException("Failed to create restaurant")
        return JSONResponse(status_code=201, content={"id": str(result.inserted_id)})
    except PyMongoError as e:
        raise DatabaseException(f"Database error: {str(e)}")
    except Exception as e:
        raise GenericException(f"Unexpected error: {str(e)}")
    
def get_restaurant_by_id(restaurant_id:str):
    """
    Retrieves a restaurant by ID.
    
    Args:
        restaurant_id (str): The ID of the restaurant to retrieve.
            Example: "60c72b2f9b1d4c3f8c8e4b1a"
    Returns:
        RestaurantInDB: The restaurant data if found.
    """
    try:
        result = restaurant_collection.find_one({"_id":ObjectId(restaurant_id)})
        result["_id"] = str(result["_id"])
        if not result:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return JSONResponse(status_code=200, content=RestaurantInDB(**result).dict(by_alias=True))
    except PyMongoError as e:
        raise DatabaseException(f"Database error: {str(e)}")
    except Exception as e:
        raise GenericException(f"Unexpected error: {str(e)}")

async def get_restaurants():
    """
    Retrieves all restaurants from the database.
    Args:
        None
    Returns:
        List[RestaurantInDB]: A list of all restaurants.
    """
    try:
        results = []
        cursor = restaurant_collection.find()
        if not cursor:
            raise NotFoundException("No restaurants found.")
        for document in cursor:
            document["_id"] = str(document["_id"])
            results.append(RestaurantInDB(**document).dict(by_alias=True))
        return JSONResponse(status_code=200, content=results)
    except PyMongoError as e:
        raise DatabaseException(f"Database error: {str(e)}")
    except Exception as e:
        raise GenericException(f"Unexpected error: {str(e)}")
    
def update_restaurant(restaurant_id:str, restaurant:RestaurantUpdate):
    """
    Updates an existing restaurant by ID.
    
    Args:
        restaurant_id (str): The ID of the restaurant to update.
            Example: "60c72b2f9b1d4c3f8c8e4b1a"
        restaurant (RestaurantUpdate): The restaurant data to update.
            Example:
            {
                "name": "Pasta Palace",
                "address": "123 Noodle St, Food City",
                "cuisine": "Italian",
                "rating":4.5
            }
    Returns:
        RestaurantInDB: The updated restaurant data.
    """
    try:
        result = restaurant_collection.update_one(
            {"_id":ObjectId(restaurant_id)},
            {"$set": restaurant.dict(exclude_unset=True)}
        )
        if result.matched_count == 0:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        if result.modified_count == 0:
            raise BadRequestException("No changes made to the restaurant.")
        updated_restaurant = restaurant_collection.find_one({"_id":ObjectId(restaurant_id)})
        updated_restaurant["_id"] = str(updated_restaurant["_id"])
        return JSONResponse(status_code=200, content=RestaurantInDB(**updated_restaurant).dict(by_alias=True))
    except PyMongoError as e:
        raise DatabaseException(f"Database error: {str(e)}")
    except Exception as e:
        raise GenericException(f"Unexpected error: {str(e)}")
    
def delete_restaurant(restaurant_id:str):
    """
    Deletes a restaurant by ID.
    Args:
        restaurant_id (str): The ID of the restaurant to delete.
            Example: "60c72b2f9b1d4c3f8c8e4b1a"
    Returns:
        dict: A message indicating successful deletion.
    """
    try:
        result = restaurant_collection.delete_one({"_id":ObjectId(restaurant_id)})
        if result.deleted_count == 0:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return JSONResponse(status_code=200, content={"message": f"Restaurant with ID {restaurant_id} deleted successfully."})
    except PyMongoError as e:
        raise DatabaseException(f"Database error: {str(e)}")
    except Exception as e:
        raise GenericException(f"Unexpected error: {str(e)}")
    


def apply_filters(query,dishes):
    logging.debug(f"Applying filters to : {dishes}")
    if not dishes:
        return []
    prompt_template = ChatPromptTemplate.from_template("""
You are a filter extraction model for a restaurant system.
Extract filters related to price, ingredients, allergens, or nutrition.

Return only JSON in this structure:
{{
  "price": {{"max": <float>, "min": <float>}},
  "ingredients": {{"include": [list], "exclude": [list]}},
  "allergens": {{"exclude": [list]}},
  "nutrition": {{"max_calories": <float>, "min_protein": <float>}}
}}

Example:
Query: "Show me dishes with chocolate but without nuts under 10 dollars."
Response:
{{
  "price": {{"max": 10, "min": 0}},
  "ingredients": {{"include": ["chocolate"], "exclude": ["nuts"]}},
  "allergens": {{"exclude": ["nuts"]}},
  "nutrition": {{}}
}}

Now analyze this query:
{query}
""")
    response =  llm.invoke(prompt_template.format_messages(query=query))
    filters = json.loads(response.content)
    logging.debug(f"Generated filters : {filters}")

    price = filters.get("price",{})
    include_ing = set(filters.get("ingredients",{}).get("include",[]))
    exclude_ing = set(filters.get("ingredients",{}).get("exclude",[]))
    exclude_allergens = set(filters.get("allergens",{}).get("exclude",[]))
    nutrition = filters.get("nutrition",{})

    def passes_nutrition_filter(dish):
        facts = dish.get("nutrition_facts", {})
        # Helper to safely get numeric values
        def get_val(key):
            return facts.get(key, {}).get("value", 0)

        # Apply nutrition-based conditions (optional, only if present)
        if "max_calories" in nutrition and get_val("calories") > nutrition["max_calories"]:
            return False
        if "min_protein" in nutrition and get_val("protein") < nutrition["min_protein"]:
            return False
        if "max_fat" in nutrition and get_val("fat") > nutrition["max_fat"]:
            return False
        if "max_carbs" in nutrition and get_val("carbohydrates") > nutrition["max_carbs"]:
            return False
        return True

    filtered = []
    for d in dishes:
        try:
            if not (price.get("min", float("-inf")) <= d.get("price", 0) <= price.get("max", float("inf"))):
                continue
            if include_ing and not include_ing.issubset(set(d.get("ingredients", []))):
                continue
            if exclude_ing and exclude_ing.intersection(set(d.get("ingredients", []))):
                continue
            if exclude_allergens and exclude_allergens.intersection(
                {a["allergen"] for a in d.get("inferred_allergens", []) + d.get("explicit_allergens", [])}
            ):
                continue
            if not passes_nutrition_filter(d):
                continue
            filtered.append(d)
        except Exception as e:
            logging.error(str(e))
            continue

    logging.debug(f"Filtered Dishes: {filtered}")
    return filtered

def validate_retrieved_dishes(query:str, dishes:list):
    if not dishes:
        return []

    prompt_template =ChatPromptTemplate.from_template("""
You are an intelligent restaurant assistant helping to filter dishes for a user query.

User query: {query}

For each of the following dishes, decide whether it matches the user's request.
Be strict but reasonable — match meaningfully relevant dishes, not partial overlaps.

Output ONLY a valid JSON list:
[
  {{"dish_id": "...", "include": true/false, "reason": "..."}},
  ...
]

Dishes:
{dishes}
""")
    response =  llm.invoke(prompt_template.format_messages(query=query,dishes=dishes))
    try:
        filtered_dish_ids = json.loads(response.content)
        logging.debug(f"Filtered Dish IDs : {filtered_dish_ids}")
        valid_ids = {item["dish_id"] for item in filtered_dish_ids if item.get("include")}
        logging.debug(f"Valid Dish IDs : {valid_ids} ")
        filtered_dishes = [d for d in dishes if d.get("_id") in valid_ids]
    except Exception as e:
        logging.error(str(e))
        filtered_dishes = []
    logging.debug(f"Filtered Dishes by LLM : {filtered_dishes}")
    return filtered_dishes
