import logging
from langgraph.graph import StateGraph
from .state import ChatState
from langgraph.constants import END
from ..services.intent_service import extract_query_intent
from ..services.retrieval_service import get_menu_items
from ..services.dish_info_service import get_dish_info
from ..services.response_synthesizer_tool import format_final_response
from ..services.context_resolver import resolve_context

logger = logging.getLogger(__name__)
# def route_branches_debugger(state):
#     print("DEBUG: state type = ",type(state))
#     print("DEBUG: state.intents = ", state.intents)

#     for idx, intent in enumerate(state.intents):
#         print(f"Intent {idx}: type = {intent.get('type')}, full = {intent}")
#     return state

def generate_query_parts(state):
    # logging.debug(f"Printing generated query parts : {state.intents}")
    # for item in state.intents:
    #     state.query_parts.setdefault(item["type"],[]).append(item["query"])
    # return state
    for item in state.intents.intents:
        state.query_parts.setdefault(item.type, []).append(item.query)
    
    return state

def route_to_menu_search(state):
    if state.query_parts.get("menu_search"):
        return "menu_retriever"
    return "last_node"

def route_to_dish_info(state):
    if state.query_parts.get("dish_info"):
        return "informative_retriever"
    return "last_node"


def last_node(state):
    logging.debug(f"Logging generated state {state}")
    return state

def create_chat_graph():
    graph = StateGraph(ChatState)

    graph.add_node("intent_classifier",extract_query_intent)
    graph.add_node("context_resolver",resolve_context)
    graph.add_node("query_part_generator",generate_query_parts)
    graph.add_node("menu_retriever",get_menu_items)
    graph.add_node("informative_retriever",get_dish_info)
    graph.add_node("format_final_response",format_final_response)
    graph.set_entry_point("intent_classifier")
    graph.add_edge("intent_classifier","context_resolver")
    graph.add_edge("context_resolver","query_part_generator")
    graph.add_edge("query_part_generator","menu_retriever")
    graph.add_edge("query_part_generator","informative_retriever")
    graph.add_edge("menu_retriever","format_final_response")
    graph.add_edge("informative_retriever","format_final_response")
    graph.set_finish_point("format_final_response")
    return graph.compile()