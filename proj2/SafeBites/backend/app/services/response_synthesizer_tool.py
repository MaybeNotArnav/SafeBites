import os
import logging
from dotenv import load_dotenv
from typing import List
from ..flow.state import ChatState
from ..models.responder_model import QueryResponse, DishResult, InfoResult, FinalResponse

load_dotenv()

logger = logging.getLogger(__name__)

def format_final_response(state:ChatState):
<<<<<<< HEAD
    logger.info(f"Formatting final response from the state {state}")
    responses : List[QueryResponse] = []

    if state.menu_results and state.menu_results.menu_results:
        for query, dishes in state.menu_results.menu_results.items():
=======
    logger.info("Formatting final response from the state....")
    responses : List[QueryResponse] = []

    if state.menu_results:
        for query, dishes in state.menu_results.items():
>>>>>>> docs/project-documentations
            responses.append(QueryResponse(
                query=query,
                type="menu_search",
                result=[DishResult(**dish) for dish in dishes]
            ))

<<<<<<< HEAD
    if state.info_results.info_results:
        for query, info in state.info_results.info_results.items():
            logger.debug(f"Printing Info results for query {query} : {info}")
            responses.append(QueryResponse(
                query=query,
                type="dish_info",
                result=InfoResult(**info.model_dump())
=======
    if state.info_results:
        for query, info in state.info_results.items():
            responses.append(QueryResponse(
                query=query,
                type="dish_info",
                result=InfoResult(**info)
>>>>>>> docs/project-documentations
            ))

    if state.query_parts and state.query_parts.get("gibberish"):
        for query in state.query_parts["gibberish"]:
            responses.append(QueryResponse(
                query=query,
                type="gibberish",
                result={"message":"Sorry, I couldn't understand your query.Pleas rephrase it."}
            ))

<<<<<<< HEAD
    logger.debug(f"Final formatted responses: {responses}")
=======
>>>>>>> docs/project-documentations
    final = FinalResponse(
        user_id=state.user_id,
        session_id=state.session_id,
        restaurant_id=state.restaurant_id,
        original_query=state.query,
        responses=responses,
        status="success" if responses else "failed"
    )
<<<<<<< HEAD
    logger.debug(f"Final Response Object: {final}")
=======
>>>>>>> docs/project-documentations
    return final