from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")  # ✅ use localhost, not 'mongo'
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["expense_tracker"]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Disconnected from MongoDB")
