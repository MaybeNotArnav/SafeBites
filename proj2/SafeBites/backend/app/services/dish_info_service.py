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
        dish = hit["dish"]
        results.append({
            "dish_name": dish.get("name", "N/A"),
            "description": dish.get("description", "N/A"),
            "price": dish.get("price", "N/A"),
            "ingredients": dish.get("ingredients", []),
            "serving_size": dish.get("serving_size", "N/A"),
            "availability": dish.get("availability", "N/A"),
            "allergens": [a['allergen'] for a in dish.get("inferred_allergens", [])],
            "nutrition_facts": dish.get("nutrition_facts", {})
        })
    logging.debug(f"Food item query results: {results}")
    return results


def get_dish_info(state):
    results = {}
    restaurant_id = state.restaurant_id
    for query in state.query_parts.get("dish_info",[]):
        logging.debug(f"Getting dish info for query: {query} and restaurant_id: {restaurant_id}")

        query = query.strip()
        query_intent = derive_dish_info_intent(query)
        logging.debug(f"Query intent: {query_intent}")
        if query_intent.get("type") == "general_knowledge":
            results[query] = handle_general_knowledge(query)  
            return {"info_results":results}
    
        dish = handle_food_item_query(query, restaurant_id=restaurant_id)
        dish = apply_filters(query,dish)
        dish = validate_retrieved_dishes(query,dish)
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
        - "dish_name"
        - "requested_info"
        - "source_data"

        User Query: {query}

        Dish Data: {context}
        """)
        response = llm.invoke(prompt.format_messages(query=query,context=context))
        logging.debug(f"LLM Response: {response.content}")
        try:
            refined = json.loads(response.content)
        except Exception as e:
            logging.error(str(e))
            refined = {"message": "Could not parse response."}

        results[query] = refined
    return {"info_results":results}