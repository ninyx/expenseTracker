from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo import MongoClient 
from mongomock import MongoClient as MockMongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")  # ✅ use localhost, not 'mongo'
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"

APP_ENV = os.getenv("APP_ENV", "development")

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["expense_tracker"]
    print("✅ Connected to MongoDB")

def get_client():
    """Return the appropriate MongoDB client depending on environment."""
    if APP_ENV == "test":
        print("[INFO] Using Mock MongoDB (mongomock) for testing.")
        return MockMongoClient()
    return MongoClient(MONGO_URL)

def get_db():
    yield db

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")
