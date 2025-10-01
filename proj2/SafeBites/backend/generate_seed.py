import requests, json, random
from faker import Faker
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

fake = Faker()

base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

# generate restaurant data
restaurants = []
num_restaurants = 3
for i in range(1,num_restaurants + 1):
    restaurants.append({
        "_id":f"rest_{i}",
        "name":fake.company() + random.choice(["Kitchen","Bistro","Cafe","Trattoria","Diner"]),
        "address":fake.address().replace("\n",", "),
        "cuisine":[random.choice(["Italian","Thai","Indian","Mexican","American","Japanese"])]
    })

def get_random_meal():
    r = requests.get("https://www.themealdb.com/api/json/v1/1/random.php")
    print("Fetching random meal...")
    j = r.json()
    m = j["meals"][0]
    ingredients = []
    for n in range(1,21):
        ing = m.get(f"strIngredient{n}")
        if ing and ing.strip():
            ingredients.append(ing)
        
    return {
        "name":m.get("strMeal") or "random_meal",
        "description":m.get("strInstructions")[:240] if m.get("strInstructions") else "",
        "ingredients":ingredients,
    }
    

dishes = []
dish_id = 1
for r in restaurants:
    for _ in range(20):
        meal = get_random_meal()
        price = round(random.uniform(6.0,28.0),2)
        dishes.append({
            "_id":f"dish_{dish_id}",
            "restaurant_id":r["_id"],
            "name":meal["name"],
            "description":meal["description"],
            "price":price,
            "ingredients":meal["ingredients"],
        })
        dish_id += 1


with open("./backend/seed_data/restaurants.json","w") as f:
    json.dump(restaurants,f,indent=2)
with open("./backend/seed_data/dishes.json","w") as f:
    json.dump(dishes,f,indent=2)


def generate_refined_res_data(dish):
    llm = ChatOpenAI(model="gpt-5", api_key=os.environ.get("OPENAI_KEY"))
    prompt_template = ChatPromptTemplate.from_template("""
You are an allergen annotator for a restaurant dish database.

Given a dish name and description,ingredients(maybe) infer ONLY:
- ingredients (as a list of words/phrases) only if they are not present,
- allergens (list of {{allergen, confidence [0–1], why}}),
- a one-line summary of the dish.

Do NOT return any other fields. 
Do NOT change dish name, description, price, or other metadata.

Allowed allergens: peanuts, tree_nuts, dairy, egg, soy, wheat_gluten, fish, shellfish, sesame.

Dish input:
Name: "{name}"
Description: "{description}"
Ingredients: "{ingredients}"

Output JSON ONLY:
{{
  "ingredients": [...],
  "inferred_allergens": [
    {{"allergen": "...", "confidence": 0.95, "why": "..."}}
  ],
  "summary": "..."
}}
""")
    
    prompt = prompt_template.format_messages(
        name=dish.get("name",""),
        description=dish.get("description",""),
        ingredients=dish.get("ingredients","")
    )

    print(prompt)
    response = llm.invoke(prompt)

    try:
        refined = json.loads(response.content)
    except Exception as e:
        print(e)
        return dish
    
    if "ingredients" not in dish or not dish["ingredients"]:
        dish["ingredients"] = refined.get("ingredients",[])
    
    if "inferred_allergens" not in dish or not dish["inferred_allergens"]:
        dish["inferred_allergens"] = refined.get("inferred_allergens",[])

    if "summary" not in dish or not dish["summary"]:
        dish["description"] = refined.get("summary","")

    dish.setdefault("availaibility",True)
    dish.setdefault("serving_size", "single")
    dish.setdefault("explicit_allergens", [])

    return dish

print(f"Generated {len(restaurants)} restaurants and {len(dishes)} dishes")

# print(dishes[0]["name"],dishes[0]["description"],dishes[0]["ingredients"])
refined_dishes = [generate_refined_res_data(d) for d in dishes]

with open("./backend/seed_data/dishes_refined.json","w") as f:
    json.dump(refined_dishes,f,indent=2)

print("Refined dish data with inferred ingredients and allergens")