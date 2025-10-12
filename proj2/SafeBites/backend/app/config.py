import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "foodapp")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "foodapp_test")
JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
