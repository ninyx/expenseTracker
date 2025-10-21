# tests/test_transaction_crud.py
import pytest
import random
from datetime import datetime, timedelta
from bson import ObjectId  # only if your MongoDB uses ObjectIds

# ---------- Utility functions ----------

def random_date():
    start = datetime.now() - timedelta(days=90)
    end = datetime.now()
    random_dt = start + (end - start) * random.random()
    return random_dt.isoformat()

def random_transaction():
    """Generate dummy transaction data."""
    types = ["income", "expense", "reimburse", "transfer"]
    ttype = random.choice(types)
    amount = round(random.uniform(100, 5000), 2)
    desc = f"Dummy {ttype} transaction"

    if ttype in ["income", "expense"]:
        return {
            "type": ttype,
            "account_uid": "acct-cash",
            "category_uid": "cat-food",
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }

    elif ttype == "transfer":
        return {
            "type": "transfer",
            "from_account_uid": "acct-bank",
            "to_account_uid": "acct-wallet",
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }

    elif ttype == "reimburse":
        return {
            "type": "reimburse",
            "account_uid": "acct-cash",
            "expense_uid": "tx-expense123",
            "amount": amount,
            "description": desc,
            "date": random_date(),
        }

# ---------- CRUD Tests ----------

@pytest.mark.asyncio
async def test_create_transaction(async_client):
    payload = random_transaction()
    response = await async_client.post("/transactions/", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["amount"] == payload["amount"]

@pytest.mark.asyncio
async def test_get_transactions(async_client):
    # First create a transaction
    payload = random_transaction()
    create_response = await async_client.post("/transactions/", json=payload)
    assert create_response.status_code == 201

    # Then get all transactions
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert isinstance(transactions, list)
    assert len(transactions) > 0

@pytest.mark.asyncio
async def test_get_transaction_by_id(async_client):
    # First create a transaction
    payload = random_transaction()
    create_response = await async_client.post("/transactions/", json=payload)
    assert create_response.status_code == 201
    created_tx = create_response.json()
    
    # Then get it by ID
    response = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == created_tx["uid"]

@pytest.mark.asyncio
async def test_update_transaction(async_client):
    # First create a transaction
    payload = random_transaction()
    create_response = await async_client.post("/transactions/", json=payload)
    assert create_response.status_code == 201
    created_tx = create_response.json()

    # Then update it
    update_payload = {"description": "Updated test transaction"}
    response = await async_client.patch(f"/transactions/{created_tx['uid']}", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["description"] == "Updated test transaction"
    assert updated["uid"] == created_tx["uid"]

@pytest.mark.asyncio
async def test_delete_transaction(async_client):
    # First create a transaction
    payload = random_transaction()
    create_response = await async_client.post("/transactions/", json=payload)
    assert create_response.status_code == 201
    created_tx = create_response.json()

    # Then delete it
    response = await async_client.delete(f"/transactions/{created_tx['uid']}")
    assert response.status_code == 200

    # Confirm it's deleted
    confirm = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert confirm.status_code == 404
