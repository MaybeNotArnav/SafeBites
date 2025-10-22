import logging

from ..models.dish_info_model import DishData
from .faiss_service import semantic_retrieve_with_negation
from .restaurant_service import apply_filters, validate_retrieved_dishes

logger = logging.getLogger(__name__)

def get_menu_items(state):
    results = {}
    restaurant_id = state.restaurant_id
    for q in state.query_parts.get("menu_search",[]):
        logging.debug(f"Retrieving menu items for query: {q} and restaurant_id: {restaurant_id}")
        try:
            hits = semantic_retrieve_with_negation(q, restaurant_id)
            logging.debug(f"Retrieved data from semantic search: {hits}")
            dish_results = [DishData(
                dish_id=hit.dish["_id"],
                dish_name=hit.dish["name"],
                description=hit.dish["description"],
                price=hit.dish["price"],
                ingredients=hit.dish["ingredients"],
                serving_size=hit.dish["serving_size"],
                availability=hit.dish["availaibility"],
                allergens=[a["allergen"] for a in hit.dish["inferred_allergens"]],
                nutrition_facts=hit.dish["nutrition_facts"]
            ) for hit in hits]

            if not dish_results:
                logger.warning(f"No dishes found for query= {q}")
                results[q] = []
                continue
            
            dish_results = apply_filters(q,dish_results)
            dish_results = validate_retrieved_dishes(q,dish_results)
        except Exception as e:
            logging.error(str(e))
            dish_results = []
        results[q] = dish_results
    return {"menu_results":results}