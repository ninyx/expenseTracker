# tests/conftest.py
"""Pytest configuration and fixtures for testing."""

import os
import asyncio
import pytest
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, ASGITransport

# Import your app and the get_db dependency
from src.server import app
from src.database import get_db

load_dotenv()

# ---------------------------
# Windows fix for Motor + asyncio
# ---------------------------
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------
# MongoDB test connection info
# ---------------------------
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root").strip()
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password").strip()
MONGO_HOST = os.getenv("MONGO_HOST", "localhost").strip()
MONGO_PORT = os.getenv("MONGO_PORT", "27017").strip()
TEST_DB_NAME = "expenseTracker_test"

MONGO_TEST_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{TEST_DB_NAME}?authSource=admin"


# ---------------------------
# Test database fixture
# ---------------------------
@pytest.fixture(scope="function")
async def test_db():
    """
    Provides a clean test database for each test.
    
    This fixture:
    1. Creates a Motor async connection to the test database
    2. Cleans all collections before each test
    3. Yields the database instance for the test
    4. Drops the database and closes connection after the test
    """
    # IMPORTANT: Use AsyncIOMotorClient for async operations
    client = AsyncIOMotorClient(
        MONGO_TEST_URL,
        serverSelectionTimeoutMS=5000
    )
    
    db = client[TEST_DB_NAME]

    # --- SETUP: Verify connection and clean database ---
    try:
        await client.admin.command('ping')
        print(f"✓ Connected to test MongoDB at {MONGO_HOST}:{MONGO_PORT}")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        client.close()
        raise

    # Clean up any existing data from previous test runs
    try:
        collections = await db.list_collection_names()
        for col in collections:
            if col != 'system.views':  # Don't drop system collections
                await db[col].delete_many({})
        if collections:
            print(f"🧹 Cleaned {len(collections)} collection(s)")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean collections: {e}")

    # Yield database to the test
    yield db

    # --- TEARDOWN: Drop database and close connection ---
    try:
        await client.drop_database(TEST_DB_NAME)
        print(f"🗑️  Dropped test database: {TEST_DB_NAME}")
    except Exception as e:
        print(f"⚠️  Warning: Could not drop database: {e}")
    finally:
        client.close()


# ---------------------------
# Async HTTP client fixture
# ---------------------------
@pytest.fixture
async def async_client(test_db):
    """
    Provides an async HTTP client for testing FastAPI endpoints.
    
    This fixture:
    1. Overrides the get_db dependency to use test_db
    2. Creates an async HTTP client
    3. Yields the client for testing
    4. Cleans up dependency overrides after the test
    """
    # Override the get_db dependency to return our test database
    async def override_get_db():
        return test_db
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create async HTTP client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Clean up: Clear dependency overrides
    app.dependency_overrides.clear()