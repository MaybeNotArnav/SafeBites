"""
MongoDB Database Connection Module

- Establishes a connection to MongoDB using the URI and database name
  from configuration.
- Provides a `db` object for direct database operations.
- `get_db()` returns the database instance for dependency injection or service use.
"""
from pymongo import MongoClient
from .config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_db():
    """Return database connection object."""
    return db
