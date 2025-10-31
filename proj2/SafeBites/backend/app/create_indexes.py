from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "SafeBitesDB"

async def create_indexes():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Users
    await db.users.create_index("username", unique=True)

    # Dishes
    await db.dishes.create_index([("restaurant_id", 1), ("dish_name", 1)])

    print("Indexes created")

    client.close()  # ✅ no await here

if __name__ == "__main__":
    asyncio.run(create_indexes())
