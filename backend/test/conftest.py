import pytest
from httpx import AsyncClient, ASGITransport
from src.server import app
from src.database import get_db
from mongomock import MongoClient

class MockDB:
    """Simple mock DB wrapper."""
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client["test_expense_tracker"]

    async def get_collection(self, name):
        return self.db[name]


@pytest.fixture
def mock_db():
    """Mock database for testing."""
    return MockDB()


@pytest.fixture
async def async_client(mock_db, monkeypatch):
    """Async test client with mock DB."""
    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
