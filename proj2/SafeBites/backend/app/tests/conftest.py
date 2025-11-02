import os
import pytest
from pymongo import MongoClient
from fastapi.testclient import TestClient

# Force tests to use test DB
os.environ.setdefault("TEST_DB_NAME", "foodapp_test")
os.environ.setdefault("DB_NAME", "foodapp_test")

from app.main import app
from app.config import MONGO_URI, TEST_DB_NAME

@pytest.fixture(scope="session")
def db_client():
    """
    Provide a synchronous MongoDB client for tests.
    Drops relevant collections before/after the entire session.
    """
    mongo = MongoClient(MONGO_URI)
    db = mongo[TEST_DB_NAME]

    # Clean collections before tests
    db.users.delete_many({})
    db.dishes.delete_many({})
    db.restaurants.delete_many({})

    yield db

    # Clean collections after tests
    db.users.delete_many({})
    db.dishes.delete_many({})
    db.restaurants.delete_many({})

    mongo.close()


@pytest.fixture(scope="session")
def client(db_client):
    """
    Provide a sync TestClient for FastAPI.
    """
    with TestClient(app) as c:
        yield c
