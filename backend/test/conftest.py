# test/conftest.py
import os
import asyncio
import pytest
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, ASGITransport
from src.server import app
from src.database import get_client, get_db

# Load environment variables
load_dotenv()

# MongoDB connection configuration
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "root").strip()
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password").strip()
MONGO_HOST = os.getenv("MONGO_HOST", "localhost").strip()
MONGO_PORT = os.getenv("MONGO_PORT", "27017").strip()
TEST_DB_NAME = "expenseTracker_test"

MONGO_TEST_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{TEST_DB_NAME}?authSource=admin"

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)

@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio to use asyncio backend."""
    return "asyncio"

@pytest.fixture(scope="function")
async def test_db(monkeypatch):
    """Provide a dedicated MongoDB test database.
    
    This fixture:
    1. Connects to the test database
    2. Cleans up existing data
    3. Yields the database for tests
    4. Cleans up after tests complete
    """
    try:
        client = AsyncIOMotorClient(MONGO_TEST_URL, serverSelectionTimeoutMS=5000)
        # Verify connection is working
        await client.admin.command('ping')
        
        db = client[TEST_DB_NAME]

        # Clean up before tests
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})

        # Override get_db to return test database
        async def mock_get_db():
            return db
        monkeypatch.setattr("src.database.get_db", mock_get_db)
        monkeypatch.setattr("src.crud.transactions.get_db", mock_get_db)

        yield db

        # Clean up after tests
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})
    
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise
    finally:
        client.close()



@pytest.fixture(scope="function")
async def async_client(test_db):
    """Provides an async HTTP client using ASGITransport with database connection."""
    # Ensure database connection is established before app startup
    app.state.db = test_db
    
    # Run FastAPI startup event
    await app.router.startup()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Run FastAPI shutdown event
    await app.router.shutdown()
