from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import StructuredTool
# from fastapi import HTTPException
from pydantic import BaseModel
from ..services.retrieval_service import get_menu_items
from ..services.response_synthesizer_tool import format_final_response
from ..services.dish_info_service import get_dish_info
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4-turbo",temperature=0.7,openai_api_key=os.getenv("OPENAI_KEY"))

class MenuQuery(BaseModel):
    query: str
    restaurant_id: str

get_menu_items_tool = StructuredTool.from_function(
    func=get_menu_items,
    name="get_menu_items",
    args_schema=MenuQuery,
    description=(
        "Search for dishes using the following parameters:\n"
        "- query: the dish or ingredient to search for along with any specific details needed\n"
        "- restaurant_id: (optional) ID of the restaurant\n"
        "- top_k: (optional) max number of results to return\n"
        "Example queries: 'show me desserts with chocolate', 'find gluten-free pizzas'."
        "Return a json containing list of hits which internally contains dish which are matching the query."
    ),
    return_direct=False,
    # args=[
    #     ToolParameter(
    #         name="query",
    #         description="The dish or ingredient to search for",
    #         type=str,
    #         required=True
    #     ),
    #     ToolParameter(
    #         name="restaurant_id",
    #         description="Restaurant ID of the restaurant",
    #         type=str,
    #         required=True
    #     ),
    # ]
)

get_dish_info_tool = StructuredTool.from_function(
    func=get_dish_info,
    name="get_dish_info",
    args_schema=MenuQuery,
    return_direct=False,
    description=(
        "Useful for when you need to find specific information about a dish, such as ingredients, allergens, or nutrition. "
        "Parameters:\n"
        "- query: the dish or ingredient to search for along with any specific details needed\n"
        "- restaurant_id: (optional) ID of the restaurant\n"
        "Example: 'does chocolate contain gluten?', 'what are the allergens in pasta carbonara?'."
        "Return a json containing dish_name, requested_info and source_data."
    ),
)


tools = [
    get_menu_items_tool,
    get_dish_info_tool,
    Tool(
        name="format_response",
        func=format_final_response,
        description=(
            "This is a mandatory final step."
            "Take the intermediate dish results or any informative info or both"
            "and format them into a fixed JSON structure suitable for frontend rendering. "
            "Always return valid JSON."
        )
    )
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agents = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    memory=memory,
    verbose=True
)