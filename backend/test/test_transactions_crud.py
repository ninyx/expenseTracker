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
    assert "id" in data or "_id" in data  # depends on your API schema

@pytest.mark.asyncio
async def test_get_transactions(async_client):
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert isinstance(transactions, list)

    if transactions:
        global FIRST_ID
        FIRST_ID = transactions[0].get("id") or transactions[0].get("_id")
        assert FIRST_ID is not None

@pytest.mark.asyncio
async def test_get_transaction_by_id(async_client):
    # requires previous test to run first
    if not globals().get("FIRST_ID"):
        pytest.skip("No transaction ID available from previous test.")
    response = await async_client.get(f"/transactions/{FIRST_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == FIRST_ID or data.get("_id") == FIRST_ID

@pytest.mark.asyncio
async def test_update_transaction(async_client):
    if not globals().get("FIRST_ID"):
        pytest.skip("No transaction ID available from previous test.")

    update_payload = {"description": "Updated test transaction"}
    response = await async_client.put(f"/transactions/{FIRST_ID}", json=update_payload)
    assert response.status_code in (200, 202)
    updated = response.json()
    assert "Updated test transaction" in updated["description"]

@pytest.mark.asyncio
async def test_delete_transaction(async_client):
    if not globals().get("FIRST_ID"):
        pytest.skip("No transaction ID available from previous test.")

    response = await async_client.delete(f"/transactions/{FIRST_ID}")
    assert response.status_code in (200, 204)

    # Confirm it's deleted
    confirm = await async_client.get(f"/transactions/{FIRST_ID}")
    assert confirm.status_code == 404
