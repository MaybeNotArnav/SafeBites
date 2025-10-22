import os
import logging
from dotenv import load_dotenv
from typing import List
from ..flow.state import ChatState
from ..models.responder_model import QueryResponse, DishResult, InfoResult, FinalResponse

load_dotenv()

logger = logging.getLogger(__name__)

def format_final_response(state:ChatState):
    logger.info(f"Formatting final response from the state {state}")
    responses : List[QueryResponse] = []

    if state.menu_results and state.menu_results.menu_results:
        for query, dishes in state.menu_results.menu_results.items():
            responses.append(QueryResponse(
                query=query,
                type="menu_search",
                result=[DishResult(**dish) for dish in dishes]
            ))

    if state.info_results.info_results:
        for query, info in state.info_results.info_results.items():
            logger.debug(f"Printing Info results for query {query} : {info}")
            responses.append(QueryResponse(
                query=query,
                type="dish_info",
                result=InfoResult(**info.model_dump())
            ))

    if state.query_parts and state.query_parts.get("gibberish"):
        for query in state.query_parts["gibberish"]:
            responses.append(QueryResponse(
                query=query,
                type="gibberish",
                result={"message":"Sorry, I couldn't understand your query.Pleas rephrase it."}
            ))

    logger.debug(f"Final formatted responses: {responses}")
    final = FinalResponse(
        user_id=state.user_id,
        session_id=state.session_id,
        restaurant_id=state.restaurant_id,
        original_query=state.query,
        responses=responses,
        status="success" if responses else "failed"
    )
    logger.debug(f"Final Response Object: {final}")
    return final