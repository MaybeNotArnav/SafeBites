from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.tools import tool
import os
from dotenv import load_dotenv
from typing import List
from ..utils.llm_tracker import LLMUsageTracker

load_dotenv()

from ..models.responder_model import UIHints, UnifiedResponse

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

parser = PydanticOutputParser(pydantic_object=UnifiedResponse)

def response_formatter_tool(query:str, dishes:List[dict],info:str = "") -> dict:
    print(f"Formatting response for query: {query} with {len(dishes)} dishes and info: {info}")
    prompt = ChatPromptTemplate.from_template("""
    You are a response formatter for a food delivery system.

    Convert the following raw data into a JSON that fits this schema:
    {format_instructions}

    User Query: {query}

    Retrieved Dishes (from FAISS / DB):
    {dishes}

    Additional Informative Info (if any):
    {info}

    Ensure:
    - Results are accurate and structured.
    - If query mentions something like calories, include it in informative_info.
    - Always return valid JSON following the schema exactly.
    """)

    formatted_prompt = prompt.format(
        query=query,
        dishes=dishes,
        info=info,
        format_instructions=parser.get_format_instructions(),
    )

    response = llm.invoke(formatted_prompt)
    try:
        structured_response = parser.parse(response.content)
    except Exception as e:
        print(f"Parsing failed: {e}")
        structured_response = UnifiedResponse(
            intent="menu_item_retrieval",
            query=query,
            results=dishes,
            informative_info=[],
            ui_hints=UIHints(component="CardGrid")
        )
    return structured_response.dict()