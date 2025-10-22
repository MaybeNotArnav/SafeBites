import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os, json
from dotenv import load_dotenv
from app.services.faiss_service import semantic_retrieve_with_negation
from .restaurant_service import apply_filters, validate_retrieved_dishes
from ..utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

def derive_dish_info_intent(query):
    logging.debug(f"Deriving intent for query: {query}")

    prompt = ChatPromptTemplate.from_template("""
                                              
You are an intent analyzer for a food assistant.

Given a query, decide whether the answer requires fetching restaurant menu data.

Possible outputs:
- "requires_menu_data" → if the question is about dishes, ingredients, allergens, calories, or menu items that might exist in the restaurant data.
- "general_knowledge" → if the question is conceptual and doesn’t depend on any restaurant data.

Query: {query}

Format the response in JSON:
- type: "requires_menu_data" or "general_knowledge"

""")
    response = llm.invoke(prompt.format_messages(query=query))
    logging.debug(f"LLM Response: {response.content}")
    try:
        refined = json.loads(response.content)
    except Exception as e:
        logging.error(str(e))
        refined = {"message": "Could not parse response."}
    return refined


def handle_general_knowledge(query):
    logging.debug(f"Handling general knowledge query: {query}")
    prompt = ChatPromptTemplate.from_template("""
You are a food assistant. Answer the following query using general food knowledge only. 
Do NOT assume restaurant-specific information unless explicitly mentioned.
Query: {query}
                                              
Format the response in JSON:
- "answer": your answer to the query
                                              """)
    response = llm.invoke(prompt.format_messages(query=query))
    logging.debug(f"LLM Response: {response.content}")
    try:
        refined = json.loads(response.content)
    except Exception as e:
        logging.error(str(e))
        refined = {"message": "Could not parse response."}
    return refined

def handle_food_item_query(query, restaurant_id=None):
    logging.debug(f"Handling food item query: {query} for restaurant_id: {restaurant_id}")
    hits = semantic_retrieve_with_negation(query, restaurant_id=restaurant_id)
    if not hits:
        return {"message": "No relevant dishes found."}
    results = []
    for hit in hits:
        dish = hit.dish
        # Retrieved dish from hit: {
        #     '_id': 'dish_5',
        #      'restaurant_id': 'rest_1',
        #       'name': 'Pizza Express Margherita', 
        #       'description': 'Classic Margherita pizza with a wheat-flour crust, tomato passata, and mozzarella, finished with basil and oregano.', 
        #       'price': 25.88, 
        #       'ingredients': ['Water', 'Sugar', 'Yeast', 'Plain Flour', 'Salt', 'Olive Oil', 'Passata', 'Mozzarella', 'Oregano', 'Basil', 'Black Pepper'], 
        #       'inferred_allergens': [{'allergen': 'wheat_gluten', 'confidence': 0.98, 'why': 'Contains plain flour made from wheat, a source of gluten.'}, {'allergen': 'dairy', 'confidence': 0.98, 'why': 'Contains mozzarella cheese (milk).'}],
        #         'nutrition_facts': {'calories': {'value': 1030, 'confidence': 0.6}, 'protein': {'value': 42, 'confidence': 0.6}, 'fat': {'value': 33, 'confidence': 0.6}, 'carbohydrates': {'value': 135, 'confidence': 0.6}, 'sugar': {'value': 10, 'confidence': 0.6}, 'fiber': {'value': 6, 'confidence': 0.6}}, 
        # 'availaibility': True, 'serving_size': 'single', 'explicit_allergens': []}
        logger.debug(f"Retrieved dish from hit: {dish}")
        results.append(DishData(
            dish_id= dish["_id"],
            dish_name=dish["name"],
            description=dish["description"],
            price=dish["price"],
            ingredients=dish["ingredients"],
            serving_size=dish["serving_size"],
            availability=dish["availaibility"],
            allergens=[a["allergen"] for a in dish["inferred_allergens"]],
            nutrition_facts=dish["nutrition_facts"]
        ))
    logging.debug(f"Food item query results: {results}")
    return results


def get_dish_info(state):
    results = {}
    restaurant_id = state.restaurant_id
    for query in state.query_parts.get("dish_info",[]):
        logging.debug(f"Getting dish info for query: {query} and restaurant_id: {restaurant_id}")
        
        try:
            intent = derive_dish_info_intent(query)
        except GenericException as e:
            results[query] = DishInfoResponse(
                dish_name=None,
                requested_info="Intent derivation failed",
                source_data=[]
            )
            continue
        
        logging.debug(f"Query intent: {intent}")
        if intent.type == "general_knowledge":
            response = handle_general_knowledge(query=query)
            results[query] = DishInfoResponse(
                dish_name=None,
                requested_info=response.answer,
                source_data=[]
            ) 
            continue
            
        try:
            dishes = handle_food_item_query(query, restaurant_id=restaurant_id)
            dishes = apply_filters(query,dishes)
            dishes = validate_retrieved_dishes(query,dishes)
        except NotFoundException as e:
            logger.error(str(e))
            results[query] = DishInfoResponse(
                dish_name=None,
                requested_info=str(e),
                source_data=[]
            )
            continue
        except Exception as e:
            logger.error(str(e))
            results[query] = DishInfoResponse(
                dish_name=None,
                requested_info=f"Unexpected error: {str(e)}",
                source_data=[]
            )
            continue
    
        context = ""
        for result in dish:
            dish = result
            context += f"""
        Dish Name: {dish.get('dish_name', 'N/A')}
        Description: {dish.get('description', 'N/A')}
        Price: {dish.get('price', 'N/A')}
        Ingredients: {', '.join(dish.get('ingredients', []))}
        Serving Size: {dish.get('serving_size', 'N/A')}
        Availability: {dish.get('availability', 'N/A')}
        Allergens: {', '.join([a for a in dish.get('allergens', [])])}
        Nutrition: {dish.get('nutrition_facts', {})}
            
        """
            
        prompt = ChatPromptTemplate.from_template("""
    You are a food information assistant.
        Using ONLY the following dish data, answer the user's query.
        Format the response as JSON:
        - "dish_name" - name of the dish being referred to.
        - "requested_info" - string answer to the user's query.
        - "source_data" - list of relevant dish data used to answer the query.

        User Query: {query}

        Dish Data: {context}
        """)
        response = llm.invoke(prompt.format_messages(query=query,context=context))
        logging.debug(f"LLM Response: {response.content}")
        try:
            refined = json.loads(response.content)
        except Exception as e:
            logger.error(str(e))
            results[query] = DishInfoResponse(
                dish_name=None,
                requested_info="Could not parse LLM Response",
                source_data=[]
            )

    # return {"info_results":results}
    logger.debug(f"Printing Info Results: {results}")
    return {"info_results":DishInfoResult(info_results=results)}