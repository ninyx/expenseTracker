# tests/test_transactions.py
import pytest

@pytest.mark.asyncio
async def test_get_transactions_empty(async_client, test_db):
    # Ensure database is empty
    await test_db["transactions"].delete_many({})
    
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_transaction(async_client):
    payload = {
    "type": "expense",
    "account_uid": "acct-cash",
    "category_uid": "cat-food",
    "amount": 50.0,
    "description": "Lunch",
    }

    response = await async_client.post("/transactions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category_uid"] == "cat-food"
    assert data["amount"] == 50.0
