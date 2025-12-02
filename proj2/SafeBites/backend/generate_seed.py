import requests, json, random
from faker import Faker
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

# Load Environment Variables
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


def clean_json_response(content: str) -> str:
    """Helper to strip markdown code blocks from LLM response"""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()

# --- 1. Generate Restaurants ---
logger.info("Generating restaurant data...")
restaurants = []
num_restaurants = 3

for i in range(1, num_restaurants + 1):
    restaurants.append({
        "_id": f"rest_{i}",
        "name": fake.company() + " " + random.choice(["Kitchen", "Bistro", "Cafe", "Trattoria", "Diner"]),
        "location": fake.address().replace("\n", ", "), # Fixed: used fake.address() and key "location"
        "cuisine": [random.choice(["Italian", "Thai", "Indian", "Mexican", "American", "Japanese"])],
        "rating": round(random.uniform(3.5, 5.0), 1)
    })

# --- 2. Generate Dishes (Raw) ---
def get_random_meal():
    try:
        r = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
        j = r.json()
        m = j["meals"][0]
        ingredients = []
        for n in range(1, 21):
            ing = m.get(f"strIngredient{n}")
            if ing and ing.strip():
                ingredients.append(ing)
        
        return {
            "name": m.get("strMeal") or "random_meal",
            "description": m.get("strInstructions")[:240] if m.get("strInstructions") else "",
            "ingredients": ingredients,
        }
    except Exception as e:
        logger.error(f"Error fetching meal: {e}")
        return {
            "name": "Generic Dish",
            "description": "A delicious random meal.",
            "ingredients": ["Salt", "Pepper", "Oil"]
        }

logger.info("Fetching dish data...")
dishes = []
dish_id = 1
for r in restaurants:
    for _ in range(5): # Reduced count for speed testing, increase to 20 later
        meal = get_random_meal()
        price = round(random.uniform(6.0, 28.0), 2)
        dishes.append({
            "_id": f"dish_{dish_id}",
            "restaurant_id": r["_id"],
            "name": meal["name"],
            "description": meal["description"],
            "price": price,
            "ingredients": meal["ingredients"],
        })
        dish_id += 1

# Ensure seed_data directory exists
seed_dir = os.path.join(base_dir, "seed_data")
os.makedirs(seed_dir, exist_ok=True)

# Write Intermediate Data
with open(os.path.join(seed_dir, "restaurants.json"), "w") as f:
    json.dump(restaurants, f, indent=2)
with open(os.path.join(seed_dir, "dishes.json"), "w") as f:
    json.dump(dishes, f, indent=2)

# --- 3. Refine Data with LLM ---
def generate_refined_res_data(dish):
    prompt_template = ChatPromptTemplate.from_template("""
    You are an allergen annotator for a restaurant dish database.

    Given a dish name, description, and ingredients, infer ONLY:
    - ingredients (clean up the list)
    - allergens (list of {{allergen, confidence [0–1], why}})
    - nutrition_facts: object with approximate nutritional numeric values
    - a one-line summary of the dish.

    Do NOT return any other fields. 
    Allowed allergens: peanuts, tree_nuts, dairy, egg, soy, wheat_gluten, fish, shellfish, sesame.

    Dish input:
    Name: "{name}"
    Description: "{description}"
    Ingredients: "{ingredients}"

    Output JSON ONLY:
    {{
      "ingredients": ["list", "of", "ingredients"],
      "inferred_allergens": [
        {{"allergen": "dairy", "confidence": 0.95, "why": "contains cheese"}}
      ],
      "nutrition_facts": {{
          "calories": {{"value": 500}},
          "protein": {{"value": 20}},
          "fat": {{"value": 15}},
          "carbohydrates": {{"value": 50}},
          "sugar": {{"value": 5}},
          "fiber": {{"value": 3}}
      }},
      "summary": "A brief summary..."
    }}
    """)
    
    prompt = prompt_template.format_messages(
        name=dish.get("name",""),
        description=dish.get("description",""),
        ingredients=dish.get("ingredients","")
    )

    try:
        response = llm.invoke(prompt)
        content = clean_json_response(response.content)
        refined = json.loads(content)
        
        # Merge refined data
        if "ingredients" not in dish or not dish["ingredients"]:
            dish["ingredients"] = refined.get("ingredients", [])
        
        # Overwrite/Update inferred fields
        dish["inferred_allergens"] = refined.get("inferred_allergens", [])
        dish["nutrition_facts"] = refined.get("nutrition_facts", {})
        
        # Use summary as description if original is too long or empty
        dish["description"] = refined.get("summary", dish["description"])

    except Exception as e:
        logger.error(f"Error refining dish {dish.get('name')}: {e}")
        # Fallback defaults
        dish.setdefault("inferred_allergens", [])
        dish.setdefault("nutrition_facts", {})

    dish.setdefault("availability", True)
    dish.setdefault("serving_size", "single")
    dish.setdefault("explicit_allergens", [])

    return dish

logger.info(f"Refining {len(dishes)} dishes with Gemini...")

refined_dishes = []
for i, dish in enumerate(dishes):
    logger.info(f"Refining dish {i+1}/{len(dishes)}: {dish['name']}")
    refined_dishes.append(generate_refined_res_data(dish))
    # Limit for testing? remove break to process all
    if i == 15: break 

with open(os.path.join(seed_dir, "dishes_refined.json"), "w") as f:
    json.dump(refined_dishes, f, indent=2)

logger.info("✅ Seed generation complete. Files saved to backend/seed_data/")