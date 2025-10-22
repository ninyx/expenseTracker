# tests/test_transactions_crud.py
import pytest
import random
import uuid
from datetime import datetime, timedelta

# ---------- Utility functions ----------

def random_date():
    """Generate a random ISO datetime string within the last 90 days."""
    start = datetime.now() - timedelta(days=90)
    end = datetime.now()
    random_dt = start + (end - start) * random.random()
    return random_dt.isoformat()


def random_transaction() -> dict:
    """Generate dummy transaction data conforming to our schema."""
    types = ["income", "expense", "transfer", "reimburse"]
    ttype = random.choice(types)
    amount = round(random.uniform(100, 5000), 2)
    desc = f"Test {ttype} transaction"
    uid = f"tx-{uuid.uuid4()}"

    base_data = {
        "uid": uid,
        "amount": amount,
        "description": desc,
        "date": random_date(),
        "type": ttype,
        "notes": f"Test note for {ttype} transaction"
    }

    if ttype in ["income", "expense"]:
        return {
            **base_data,
            "account_uid": "acct-test",
            "category_uid": "cat-test",
        }
    elif ttype == "transfer":
        return {
            **base_data,
            "from_account_uid": "acct-src",
            "to_account_uid": "acct-dst",
        }
    else:  # reimburse
        return {
            **base_data,
            "account_uid": "acct-test",
            "expense_uid": "tx-exp-test",
        }


# ---------- CRUD Tests ----------

@pytest.mark.asyncio
async def test_create_transaction(async_client, test_db):
    """Test creating a new transaction."""
    payload = random_transaction()
    response = await async_client.post("/transactions/", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["amount"] == payload["amount"]
    assert data["type"] == payload["type"]
    assert data["description"] == payload["description"]
    assert "uid" in data
    assert "date" in data
    
    # Verify it was actually saved to the database
    saved_tx = await test_db.transactions.find_one({"uid": data["uid"]})
    assert saved_tx is not None
    assert saved_tx["amount"] == payload["amount"]


@pytest.mark.asyncio
async def test_get_transactions(async_client, test_db):
    """Test retrieving all transactions."""
    # Initially should be empty
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 0, "Database should be empty initially"

    # Create 3 transactions
    payloads = [random_transaction() for _ in range(3)]
    created_uids = []
    
    for payload in payloads:
        res = await async_client.post("/transactions/", json=payload)
        assert res.status_code == 201, f"Failed to create transaction: {res.text}"
        created_uids.append(res.json()["uid"])

    # Retrieve all transactions
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3, f"Expected 3 transactions, got {len(transactions)}"
    
    # Verify structure of each transaction
    for tx in transactions:
        assert all(key in tx for key in ["uid", "type", "amount", "description", "date"])
    
    # Verify all created UIDs are present
    retrieved_uids = [tx["uid"] for tx in transactions]
    for uid in created_uids:
        assert uid in retrieved_uids, f"Created UID {uid} not found in retrieved transactions"


@pytest.mark.asyncio
async def test_get_transaction_by_uid(async_client, test_db):
    """Test retrieving a single transaction by UID."""
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    assert create_res.status_code == 201
    created_tx = create_res.json()

    # Retrieve by UID
    res = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert res.status_code == 200
    data = res.json()
    assert data["uid"] == created_tx["uid"]
    assert data["amount"] == created_tx["amount"]
    assert data["type"] == created_tx["type"]
    assert data["description"] == created_tx["description"]


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(async_client, test_db):
    """Test retrieving a transaction that doesn't exist."""
    fake_uid = f"tx-{uuid.uuid4()}"
    res = await async_client.get(f"/transactions/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_transaction(async_client, test_db):
    """Test updating an existing transaction."""
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    assert create_res.status_code == 201
    created_tx = create_res.json()

    # Update specific fields
    update_payload = {
        "description": "Updated transaction",
        "amount": 999.99,
    }

    res = await async_client.patch(f"/transactions/{created_tx['uid']}", json=update_payload)
    assert res.status_code == 200, f"Update failed: {res.text}"
    
    updated = res.json()
    assert updated["description"] == update_payload["description"]
    assert updated["amount"] == update_payload["amount"]
    assert updated["type"] == created_tx["type"]  # unchanged
    assert updated["uid"] == created_tx["uid"]  # unchanged
    
    # Verify update in database
    db_tx = await test_db.transactions.find_one({"uid": created_tx["uid"]})
    assert db_tx["description"] == update_payload["description"]
    assert db_tx["amount"] == update_payload["amount"]


@pytest.mark.asyncio
async def test_update_nonexistent_transaction(async_client, test_db):
    """Test updating a transaction that doesn't exist."""
    fake_uid = f"tx-{uuid.uuid4()}"
    update_payload = {"description": "This should fail"}
    
    res = await async_client.patch(f"/transactions/{fake_uid}", json=update_payload)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_transaction(async_client, test_db):
    """Test deleting a transaction."""
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    assert create_res.status_code == 201
    created_tx = create_res.json()

    # Delete the transaction
    res = await async_client.delete(f"/transactions/{created_tx['uid']}")
    assert res.status_code == 200, f"Delete failed: {res.text}"
    
    delete_data = res.json()
    assert delete_data["status"] == "deleted"
    assert delete_data["uid"] == created_tx["uid"]

    # Verify it's deleted from the API
    get_res = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert get_res.status_code == 404

    # Verify it's deleted from the database
    db_tx = await test_db.transactions.find_one({"uid": created_tx["uid"]})
    assert db_tx is None, "Transaction should be deleted from database"


@pytest.mark.asyncio
async def test_delete_nonexistent_transaction(async_client, test_db):
    """Test deleting a transaction that doesn't exist."""
    fake_uid = f"tx-{uuid.uuid4()}"
    res = await async_client.delete(f"/transactions/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_transaction_validation(async_client, test_db):
    """Test transaction validation for invalid data."""
    # Test invalid transaction type
    invalid_payload = random_transaction()
    invalid_payload["type"] = "invalid_type"
    res = await async_client.post("/transactions/", json=invalid_payload)
    assert res.status_code == 422, "Should reject invalid transaction type"

    # Test incomplete payload (missing required fields)
    incomplete_payload = {"description": "Missing fields"}
    res = await async_client.post("/transactions/", json=incomplete_payload)
    assert res.status_code == 422, "Should reject incomplete payload"

    # Test invalid amount (negative)
    invalid_amount = random_transaction()
    invalid_amount["amount"] = -100
    res = await async_client.post("/transactions/", json=invalid_amount)
    assert res.status_code == 422, "Should reject negative amount"

    # Test missing required fields based on transaction type
    income_missing_account = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 100,
        "description": "Income without account",
        "date": random_date(),
        "type": "income",
        # Missing account_uid and category_uid
    }
    res = await async_client.post("/transactions/", json=income_missing_account)
    assert res.status_code == 422, "Should reject income without account_uid"


@pytest.mark.asyncio
async def test_transaction_types(async_client, test_db):
    """Test all transaction types can be created."""
    # Test income
    income = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 1000,
        "description": "Salary",
        "date": random_date(),
        "type": "income",
        "account_uid": "acct-checking",
        "category_uid": "cat-salary",
    }
    res = await async_client.post("/transactions/", json=income)
    assert res.status_code == 201

    # Test expense
    expense = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 50,
        "description": "Groceries",
        "date": random_date(),
        "type": "expense",
        "account_uid": "acct-checking",
        "category_uid": "cat-food",
    }
    res = await async_client.post("/transactions/", json=expense)
    assert res.status_code == 201

    # Test transfer
    transfer = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 200,
        "description": "Transfer to savings",
        "date": random_date(),
        "type": "transfer",
        "from_account_uid": "acct-checking",
        "to_account_uid": "acct-savings",
    }
    res = await async_client.post("/transactions/", json=transfer)
    assert res.status_code == 201

    # Test reimburse
    reimburse = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 75,
        "description": "Reimbursement",
        "date": random_date(),
        "type": "reimburse",
        "account_uid": "acct-checking",
        "expense_uid": "tx-expense-001",
    }
    res = await async_client.post("/transactions/", json=reimburse)
    assert res.status_code == 201

    # Verify all 4 transactions exist
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 4