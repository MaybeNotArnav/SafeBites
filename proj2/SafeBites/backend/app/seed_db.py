import json
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables (to get MONGO_URI)
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI or not DB_NAME:
    print("Error: MONGO_URI or DB_NAME not found in .env file.")
    exit(1)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def seed_database():
    # Paths to your generated JSON files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    restaurants_path = os.path.join(base_dir, "seed_data", "restaurants.json")
    dishes_path = os.path.join(base_dir, "seed_data", "dishes_refined.json")

    # 1. Seed Restaurants
    if os.path.exists(restaurants_path):
        with open(restaurants_path, "r", encoding="utf-8") as f:
            restaurants = json.load(f)
            if restaurants:
                # Optional: Clear existing data to avoid duplicates
                db["restaurants"].delete_many({}) 
                db["restaurants"].insert_many(restaurants)
                print(f"✅ Inserted {len(restaurants)} restaurants.")
    else:
        print(f"⚠️  File not found: {restaurants_path}")

    # 2. Seed Dishes
    if os.path.exists(dishes_path):
        with open(dishes_path, "r", encoding="utf-8") as f:
            dishes = json.load(f)
            if dishes:
                db["dishes"].delete_many({})
                db["dishes"].insert_many(dishes)
                print(f"✅ Inserted {len(dishes)} dishes.")
    else:
        print(f"⚠️  File not found: {dishes_path}")

if __name__ == "__main__":
    seed_database()