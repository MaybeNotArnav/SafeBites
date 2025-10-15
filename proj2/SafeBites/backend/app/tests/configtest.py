import os
import asyncio
import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

# ensure tests use test DB
os.environ.setdefault("TEST_DB_NAME", "foodapp_test")
os.environ.setdefault("DB_NAME", "foodapp_test")

from app.main import app
from app.config import MONGO_URI, TEST_DB_NAME

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    # ensure test DB is clean
    mongo = AsyncIOMotorClient(MONGO_URI)
    db = mongo[TEST_DB_NAME]
    await db.users.delete_many({})
    await db.dishes.delete_many({})
    await db.restaurants.delete_many({})

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

    # cleanup after tests
    await db.users.delete_many({})
    await db.dishes.delete_many({})
    await db.restaurants.delete_many({})
    mongo.close()