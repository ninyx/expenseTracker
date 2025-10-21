# tests/test_transactions.py
import pytest

@pytest.mark.asyncio
async def test_get_transactions_empty(async_client):
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_transaction(async_client):
    payload = {
        "account": "Cash",
        "category": "Food",
        "amount": 50.0,
        "description": "Lunch"
    }
    response = await async_client.post("/transactions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Food"
    assert data["amount"] == 50.0
