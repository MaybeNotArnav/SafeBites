import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os, json
from dotenv import load_dotenv
from ..utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)

load_dotenv()

llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])

def extract_query_intent(state):
    query = state.query
    logging.debug(f"Extracting intents for query: {query}")
    prompt = ChatPromptTemplate.from_template("""
You are an expert at splitting complex food-related user queries into independent, actionable components.

Your task is to take any user query and produce a JSON object containing three keys:

1. "menu_search" → a list of self-contained queries that ask for dishes, meals, or items.  
2. "dish_info" → a list of self-contained queries that ask for information about dishes (ingredients, calories, allergens, price, etc.)  
3. "irrelevant" → a list of queries or parts that are unrelated to food or restaurant services.

⚡ Important rules:
- Each query part must be **self-contained**: if a query depends on previous results, include that dependency explicitly.  
- Preserve **order of dependency**: queries that must be processed sequentially should include phrases like “from the dishes above” or “from the previous results”.  
- Split all queries clearly and avoid ambiguity.  
- Respond only in valid JSON, nothing else.

---

Example 1:

User Query: "Provide me a list of five chocolate dishes less than $20. Calculate the total price to buy all of them. Also, are there any dishes less than $5? If yes, how much calories does each one of them contains?"

Output:
{{
  "menu_search": [
    "List five chocolate dishes under $20",
    "List dishes under $5"
  ],
  "dish_info": [
    "Calculate the total price of the five chocolate dishes under $20",
    "Provide the calories of the dishes under $5"
  ],
  "irrelevant": []
}}

---

Example 2:

User Query: "Do you have vegan pasta options? Also, what are your opening hours? Ignore seafood dishes."

Output:
{{
  "menu_search": [
    "List vegan pasta options excluding seafood dishes"
  ],
  "dish_info": [],
  "irrelevant": [
    "What are your opening hours?"
  ]
}}

---

Example 3:

User Query: "I want a chocolate cake. By the way, tell me a joke."

Output:
{{
  "menu_search": [
    "List chocolate cakes"
  ],
  "dish_info": [],
  "irrelevant": [
    "Tell me a joke"
  ]
}}

---

Now analyze this user query and split it into independent parts:

{query}
""")
    response = llm.invoke(prompt.format_messages(query=query))
    try:
        data = json.loads(response.content)
    except:
        data = {"intents": ["irrelevant"]}
    
    logging.debug(f"Extracted intents: {data}")
    results = []
    for intent_type, queries in data.items():
        for q in queries:
            results.append({
                "type":intent_type,
                "query":q
            })
    return {"intents":results}