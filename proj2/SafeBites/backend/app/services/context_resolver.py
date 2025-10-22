from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os, json
import logging
from dotenv import load_dotenv
from ..utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

def resolve_context(state):
    if not state.context:
        return {
            "query":state.query
        }
    
    prompt_template = ChatPromptTemplate.from_template("""
You are a context resolver for a food delivery assistant.
Your job is to interpret the current user query in the context of prior conversation.

User query: {query}

Previous Context : 
{context}

If the user query refers to something previously mentioned (e.g., "that", "those", "it"),
resolve what it refers to using the most relevant prior results.

Return only the rewritten query text.
""")
    
    response = llm.invoke(prompt_template.format_messages(
        query=state.query,
        context=state.context or {}
    ))
    print("Resolved Context Response:", response.content)
    return response.strip()