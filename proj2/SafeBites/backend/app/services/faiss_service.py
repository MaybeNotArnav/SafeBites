import logging
from datetime import datetime
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
import json
import faiss
import pickle
import numpy as np
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from ..utils.llm_tracker import LLMUsageTracker

logger = logging.getLogger(__name__)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# db = get_db()

from pymongo import MongoClient
# from ..config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
dish_collection = db["dishes"]


embeddings = OpenAIEmbeddings(model="text-embedding-3-large",openai_api_key=os.getenv("OPENAI_KEY"))
embedding_dim = 1536
llm = ChatOpenAI(model="gpt-5",temperature=1,openai_api_key=os.getenv("OPENAI_KEY"),callbacks=[LLMUsageTracker()])
    

def extract_query_intent(query):
    logging.debug(f"Extracting intents for query: {query}")
    intent_prompt = ChatPromptTemplate.from_template("""
    You are an intent extraction expert for food-related natural language queries.

    Your job is to split the query into two lists:
    1. **Positive intents** — what the user explicitly wants or is open to.
       - Expand this list semantically (include closely related dishes, cuisines, or styles).
    2. **Negative intents** — what the user explicitly wants to exclude or avoid.
       - DO NOT over-expand. Keep this list narrowly focused on the specific items, ingredients, or categories mentioned.
       - Avoid including loosely related or parent-category terms.
       - Only include synonyms or direct variants (e.g., "meatballs" → ["meatball", "meat balls", "polpette"], not "beef" or "meat").

    Return the result as **valid JSON**:
    {{"positive": [...], "negative": [...]}}

    Example 1:
    Query: "Gluten-free dishes without cheese"
    Output: {{"positive": ["anything", "gluten-free"], "negative": ["cheese", "dairy cheese", "cheddar", "mozzarella"]}}

    Example 2:
    Query: "Pasta dishes without meatballs"
    Output: {{"positive": ["pasta dishes", "pasta", "spaghetti", "penne", "fettuccine"], "negative": ["meatballs", "meatball", "meat balls", "polpette"]}}

    Example 3:
    Query: "Anything but seafood"
    Output: {{"positive": ["anything", "non-seafood", "meat and poultry", "vegetarian", "vegan"], "negative": ["seafood", "fish", "shellfish", "prawns", "crab"]}}

    Query: {query}
""")
    response =  llm.invoke(intent_prompt.format_messages(query=query))
    try:
        intents = json.loads(response.content)
    except Exception as e:
        logging.error(str(e))
        intents = {"positive":[query],"negative":[]}
    return intents


def create_faiss_index(json_path = "./seed_data/dishes_refined.json"):
        with open(json_path, "r",encoding="utf-8") as f:
            refined_dishes = json.load(f)
        texts = []
        metadatas = []
        for i,dish in enumerate(refined_dishes):
            text = f"""
    Dish Name: {dish.get("name", "")}
Description: {dish.get("description", "")}
Price: {dish.get("price", "N/A")}
Ingredients: {', '.join(dish.get("ingredients", []))}
Serving Size: {dish.get("serving_size", "")}
Availability: {dish.get("availability", True)}
Allergens: {', '.join([a.get("allergen", "") for a in dish.get("inferred_allergens", [])])}
Nutrition: {dish.get("nutrition_facts", {})}
"""
            texts.append(text)

            metadata = {
                "dish_id":dish["_id"],
                "restaurant_id":dish["restaurant_id"],
                "vector_id":i
            }

            metadatas.append(metadata)
        vector_store = FAISS.from_texts(
            texts=texts,
            embedding = embeddings,
            metadatas=metadatas,
        )

        vector_store.save_local("faiss_index_restaurant")
        logging.info("FAISS index created and saved locally.")

def search_dishes(query, restaurant_id=None,top_k=20,threshold=0.8):
    vector_store = FAISS.load_local("faiss_index_restaurant", embeddings,allow_dangerous_deserialization=True)
    filter_dict = {"restaurant_id":restaurant_id} if restaurant_id else None
    results = vector_store.similarity_search_with_score(query, k=top_k, filter=filter_dict)
    structured_res = []
    for res,score in results:
        if score >= threshold:
            dish = dish_collection.find_one({"_id":res.metadata["dish_id"]})
            if dish:
                structured_res.append({
                    "dish":dish,
                    "score":score,
                    "embedding":vector_store.index.reconstruct(res.metadata["vector_id"])
                })
    return structured_res


def refine_with_centroid(dish_hits,positive_intents,dish_embeddings):
    centroid = np.mean([embeddings.embed_query(intent) for intent in positive_intents],axis=0)
    logging.debug(f"Centroid: {centroid}")
    refined = []
    for hit in dish_hits:
        dish_emb = dish_embeddings.get(hit["dish"]["_id"])
        if dish_emb is not None:
            sim = cosine_similarity(centroid.reshape(1, -1), dish_emb.reshape(1, -1))[0][0]
            if sim > 0.30:
                hit["centroid_similarity"] = sim
                refined.append(hit)
    
    refined.sort(key=lambda x: x["centroid_similarity"], reverse=True)
    return refined

def semantic_retrieve_with_negation(query,restaurant_id=None):
    logging.debug(f"Semantic retrieve called with query: {query} and restaurant_id: {restaurant_id}")
    intents = extract_query_intent(query)
    pos_hits, neg_hits = [],[]

    for p in intents["positive"]:
        pos_hits.extend(search_dishes(p,restaurant_id=restaurant_id))
    for n in intents["negative"]:
        neg_hits.extend(search_dishes(n,restaurant_id=restaurant_id))

    neg_ids = set([hit["dish"]["_id"] for hit in neg_hits])
    filtered_dishes = [hit for hit in pos_hits if hit["dish"]["_id"] not in neg_ids]

    seen = set()
    unique_filtered_dishes = []
    for hit in filtered_dishes:
        if hit["dish"]["_id"] not in seen:
            unique_filtered_dishes.append(hit)
            seen.add(hit["dish"]["_id"])

    dish_embeddings = {hit["dish"]["_id"]:hit["embedding"] for hit in unique_filtered_dishes}

    refined = refine_with_centroid(unique_filtered_dishes,intents["positive"],dish_embeddings)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "restaurant_id": restaurant_id,
        "intents": intents,
        "positive_dish_count": len(pos_hits),
        "negative_dish_count": len(neg_hits),
        "filtered_dish_count": len(unique_filtered_dishes),
        "positive_dishes": [hit["dish"].get("name", str(hit["dish"])) for hit in pos_hits],
        "negative_dishes": [hit["dish"].get("name", str(hit["dish"])) for hit in neg_hits],
        "unique_filtered_dishes": [hit["dish"].get("name", str(hit["dish"])) for hit in unique_filtered_dishes],
        "refined_dishes": [hit["dish"].get("name", str(hit["dish"])) for hit in refined]
    }

    try:
        # Append to existing file if exists
        with open("intent_dishes_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2))
            f.write(",\n")
    except Exception as e:
        logging.error(f"Logging failed: {e}")

    return refined



if __name__ == "__main__":
    create_faiss_index()