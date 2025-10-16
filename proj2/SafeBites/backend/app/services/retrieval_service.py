import logging
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
            dish_results = [res["dish"] for res in hits]
            dish_results = apply_filters(q,dish_results)
            dish_results = validate_retrieved_dishes(q,dish_results)
        except Exception as e:
            logging.error(str(e))
            dish_results = []
        results[q] = dish_results
    return {"menu_results":results}