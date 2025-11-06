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

def generate_query_parts(state):
    for item in state.intents.intents:
        state.query_parts.setdefault(item.type, []).append(item.query)
    
    return state

def create_chat_graph():
    graph = StateGraph(ChatState)

    graph.add_node("intent_classifier",extract_query_intent)
    graph.add_node("context_resolver",resolve_context)
    graph.add_node("query_part_generator",generate_query_parts)
    graph.add_node("menu_retriever",get_menu_items)
    graph.add_node("informative_retriever",get_dish_info)
    graph.add_node("format_final_response",format_final_response)
    graph.set_entry_point("context_resolver")
    graph.add_edge("context_resolver","intent_classifier")
    graph.add_edge("intent_classifier","query_part_generator")
    graph.add_edge("query_part_generator","menu_retriever")
    graph.add_edge("query_part_generator","informative_retriever")
    graph.add_edge("menu_retriever","format_final_response")
    graph.add_edge("informative_retriever","format_final_response")
    graph.set_finish_point("format_final_response")
    return graph.compile()