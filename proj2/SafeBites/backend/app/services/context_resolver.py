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
    logger.debug(f"Resolving context for state: {state}")
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
    logger.debug("Rewritten Query:", response.content)
    # return {"query": response.content.strip()}

    rewritten_query = response.content.strip().strip()

    context_summary_prompt = ChatPromptTemplate.from_template("""
You are summarizing conversation context for another LLM.
Given the following context, extract only relevant information that might help answer the query below.

Context: {context}
Query: {query}

Return a short, factual summary (under 300 words) describing relevant dishes, filters, or results.
""")
    
    summary_response = llm.invoke(context_summary_prompt.format_messages(
        context=state.context or {},
        query=rewritten_query
    ))

    current_context = summary_response.content.strip()

    logger.debug(f"Resolved Context Response: {current_context}")

    return {
        "query": rewritten_query,
        "current_context": current_context
    }