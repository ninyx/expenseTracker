from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from mongomock import MongoClient as MockMongoClient
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
APP_ENV = os.getenv("APP_ENV", "development")
DB_NAME = "expenseTracker_test" if os.getenv("APP_ENV") == "test" else "expenseTracker"

MONGO_URI = os.getenv("MONGO_URI")

# Global client and db
client = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB — mock for tests, real async client otherwise."""
    global client, db

    APP_ENV = os.getenv("APP_ENV", "development")

    if APP_ENV == "test":
        print("[INFO] Using MockMongoClient for testing")
        client = MockMongoClient()
    else:
        loop = asyncio.get_running_loop()
        client = AsyncIOMotorClient(
            MONGO_URI
        )
    print(MONGO_URI)
    db = client[DB_NAME]
    print("✅ Connected to MongoDB")

    return client

async def get_db():
    """Return the current MongoDB database (sync for test, async for dev/prod)."""
    global db, client
    if db is None:
        # fallback connection if connect_to_mongo() not yet called
        await connect_to_mongo()
    return db

async def get_client():
    """Return the current MongoDB client (sync for test, async for dev/prod)."""
    global client
    if client is None:
        # fallback connection if connect_to_mongo() not yet called
        await connect_to_mongo()
    return client

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")
