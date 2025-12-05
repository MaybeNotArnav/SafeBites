from datetime import datetime
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
import json
import numpy as np
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
dish_collection = db["dishes"]

# Switch to Google Embeddings (Dimension: 768)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
embedding_dim = 768 

def clean_json_string(json_str):
    """Helper to clean markdown code blocks often returned by Gemini"""
    json_str = json_str.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    return json_str.strip()

def derive_dish_info_intent(query):
    print(f"Deriving intent for query: {query}")

    prompt = ChatPromptTemplate.from_template("""
    You are an intent analyzer for a food assistant.

    Given a query, decide whether the answer requires fetching restaurant menu data.

    Possible outputs:
    - "requires_menu_data" → if the question is about dishes, ingredients, allergens, calories, or menu items that might exist in the restaurant data.
    - "general_knowledge" → if the question is conceptual and doesn’t depend on any restaurant data.

    Query: {query}

    Format the response in JSON:
    {{ "type": "requires_menu_data" }} OR {{ "type": "general_knowledge" }}
    """)
    
    # Use Gemini Flash
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    response = llm.invoke(prompt.format_messages(query=query))
    print(f"LLM Response: {response.content}")
    try:
        content = clean_json_string(response.content)
        refined = json.loads(content)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Response content:", response.content)
        refined = {"message": "Could not parse response."}
    return refined


def handle_general_knowledge(query):
    print(f"Handling general knowledge query: {query}")

    prompt = ChatPromptTemplate.from_template("""
    You are a food assistant. Answer the following query using general food knowledge only. 
    Do NOT assume restaurant-specific information unless explicitly mentioned.
    Query: {query}
                                                
    Format the response in JSON:
    {{ "answer": "your answer to the query" }}
    """)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    response = llm.invoke(prompt.format_messages(query=query))
    print(f"LLM Response: {response.content}")
    try:
        content = clean_json_string(response.content)
        refined = json.loads(content)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Response content:", response.content)
        refined = {"message": "Could not parse response."}
    return refined

def handle_food_item_query(query, restaurant_id=None):
    print(f"Handling food item query: {query} for restaurant_id: {restaurant_id}")
    hits = semantic_retrieve_with_negation(query, restaurant_id=restaurant_id)
    if not hits:
        return {"message": "No relevant dishes found."}
    results = []
    for hit in hits:
        dish = hit["dish"]
        results.append({
            "dish_name": dish.get("name", "N/A"),
            "description": dish.get("description", "N/A"),
            "price": dish.get("price", "N/A"),
            "ingredients": dish.get("ingredients", []),
            "serving_size": dish.get("serving_size", "N/A"),
            "availability": dish.get("availability", "N/A"),
            "allergens": [a['allergen'] for a in dish.get("inferred_allergens", [])],
            "nutrition_info": dish.get("nutrition_info", {})
        })
    print(f"Food item query results: {results}")
    return results


def get_dish_info(query, restaurant_id=None):
    print(f"Getting dish info for query: {query} and restaurant_id: {restaurant_id}")

    query = query.strip()
    query_intent = derive_dish_info_intent(query)
    print(f"Query intent: {query_intent}")
    if query_intent.get("type") == "general_knowledge":
        return handle_general_knowledge(query)
    
    dish = handle_food_item_query(query, restaurant_id=restaurant_id)
    
    context = ""
    for result in dish:
        # Note: 'dish' is the list, 'result' is the item. Variable naming in original code was slightly confusing but kept logic intact.
        d_item = result
        print(d_item)
        context += f"""
    Dish Name: {d_item.get('dish_name', 'N/A')}
    Description: {d_item.get('description', 'N/A')}
    Price: {d_item.get('price', 'N/A')}
    Ingredients: {', '.join(d_item.get('ingredients', []))}
    Serving Size: {d_item.get('serving_size', 'N/A')}
    Availability: {d_item.get('availability', 'N/A')}
    Allergens: {', '.join([str(a) for a in d_item.get('allergens', [])])}
    Nutrition: {d_item.get('nutrition_info', {})}
        """
    print(f"Context for LLM: {context}")
        
    prompt = ChatPromptTemplate.from_template("""
    You are a food information assistant.
    Using ONLY the following dish data, answer the user's query.
    Format the response as JSON:
    {{
        "dish_name": "name",
        "requested_info": "info",
        "source_data": "data"
    }}

    User Query: {query}
    Dish Data: {context}
    """)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    response = llm.invoke(prompt.format_messages(query=query, context=context))
    print(f"LLM Response: {response.content}")
    try:
        content = clean_json_string(response.content)
        refined = json.loads(content)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print("Response content:", response.content)
        refined = {"message": "Could not parse response."}
    return refined


def extract_query_intent(query):
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    intent_prompt = ChatPromptTemplate.from_template("""
    You are an intent extraction expert for food-related natural language queries.

    Your job is to split the query into two lists:
    1. **Positive intents** — what the user explicitly wants or is open to.
    2. **Negative intents** — what the user explicitly wants to exclude or avoid.

    Return the result as **valid JSON**:
    {{"positive": [...], "negative": [...]}}

    Query: {query}
    """)
    
    response = llm.invoke(intent_prompt.format_messages(query=query))
    try:
        content = clean_json_string(response.content)
        intents = json.loads(content)
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Response content:", response.content)
        intents = {"positive": [query], "negative": []}
    return intents


def create_faiss_index():
    texts = []
    metadatas = []
    
    print("Fetching dishes from DB to rebuild index...")
    for i, dish in enumerate(dish_collection.find()):
        text = f"""
Dish Name : {dish.get("name", "")}
Description : {dish.get("description", "")}
Price : {dish.get("price", "")}
Ingredients : {', '.join(dish.get("ingredients", []))}
Serving Size : {dish.get("serving_size", "")}
Availability : {dish.get("availability", True)}
Allergens : {', '.join([a.get("allergen", "") for a in dish.get("inferred_allergens", [])])}
Nutrition : {dish.get("nutrition_info", {})}
"""
        texts.append(text)

        metadata = {
            "dish_id": dish["_id"],
            "restaurant_id": dish["restaurant_id"],
            "vector_id": i
        }
        metadatas.append(metadata)

    if not texts:
        print("No dishes found to index.")
        return

    vector_store = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
    )

    vector_store.save_local("faiss_index_restaurant")
    print("FAISS index created and saved locally using Gemini embeddings.")

def search_dishes(query, restaurant_id=None, top_k=20, threshold=0.8):
    try:
        vector_store = FAISS.load_local("faiss_index_restaurant", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Could not load FAISS index: {e}")
        return []

    filter_dict = {"restaurant_id": restaurant_id} if restaurant_id else None
    results = vector_store.similarity_search_with_score(query, k=top_k, filter=filter_dict)
    structured_res = []
    
    for res, score in results:
        # FAISS score is L2 distance, closer to 0 is better. 
        # However, if using cosine similarity via LangChain wrapper, logic might vary.
        # Assuming typical setup where lower score = better match, or if normalized.
        # Adjust threshold logic based on specific embedding behavior if needed.
        if score < threshold: # Check logic: usually score is distance. 
             pass 

        dish = dish_collection.find_one({"_id": res.metadata["dish_id"]})
        if dish:
            structured_res.append({
                "dish": dish,
                "score": score,
                "embedding": vector_store.index.reconstruct(res.metadata["vector_id"])
            })
    return structured_res


def refine_with_centroid(dish_hits, positive_intents, dish_embeddings):
    if not positive_intents:
        return dish_hits

    centroid = np.mean([embeddings.embed_query(intent) for intent in positive_intents], axis=0)
    print("Centroid shape:", centroid.shape)
    
    refined = []
    for hit in dish_hits:
        dish_emb = dish_embeddings.get(hit["dish"]["_id"])
        
        if dish_emb is not None:
            # Reshape for sklearn cosine_similarity
            sim = cosine_similarity(centroid.reshape(1, -1), dish_emb.reshape(1, -1))[0][0]
            print(f"Similarity for {hit['dish'].get('name')}: {sim}")
            
            if sim > 0.45:
                hit["centroid_similarity"] = sim
                refined.append(hit)
    
    refined.sort(key=lambda x: x["centroid_similarity"], reverse=True)
    return refined

def semantic_retrieve_with_negation(query, restaurant_id=None):
    intents = extract_query_intent(query)
    pos_hits, neg_hits = [], []

    for p in intents["positive"]:
        pos_hits.extend(search_dishes(p, restaurant_id=restaurant_id))
    for n in intents["negative"]:
        neg_hits.extend(search_dishes(n, restaurant_id=restaurant_id))

    neg_ids = set([hit["dish"]["_id"] for hit in neg_hits])
    filtered_dishes = [hit for hit in pos_hits if hit["dish"]["_id"] not in neg_ids]

    seen = set()
    unique_filtered_dishes = []
    for hit in filtered_dishes:
        if hit["dish"]["_id"] not in seen:
            unique_filtered_dishes.append(hit)
            seen.add(hit["dish"]["_id"])

    dish_embeddings = {hit["dish"]["_id"]: hit["embedding"] for hit in unique_filtered_dishes}

    refined = refine_with_centroid(unique_filtered_dishes, intents["positive"], dish_embeddings)
    
    # Simple logging (stripped down for brevity)
    print(f"Refined {len(refined)} dishes from {len(unique_filtered_dishes)} filtered candidates.")

    return refined

if __name__ == "__main__":
    # Ensure you run this once to rebuild index with new embeddings!
    # create_faiss_index()
    
    # Test
    print(get_dish_info("What are the different kind of hotdogs in this world?", restaurant_id="rest_1"))