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
    }

    if ttype in ["income", "expense"]:
        return {**base_data, "account_uid": "acct-test", "category_uid": "cat-test"}
    elif ttype == "transfer":
        return {**base_data, "from_account_uid": "acct-src", "to_account_uid": "acct-dst"}
    else:  # reimburse
        return {**base_data, "account_uid": "acct-test", "expense_uid": "tx-exp-test"}


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
    assert "uid" in data and "date" in data
    
    saved_tx = await test_db.transactions.find_one({"uid": data["uid"]})
    assert saved_tx is not None
    assert saved_tx["amount"] == payload["amount"]


@pytest.mark.asyncio
async def test_get_transactions(async_client, test_db):
    """Test retrieving all transactions."""
    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    assert response.json() == [], "Database should be empty initially"

    payloads = [random_transaction() for _ in range(3)]
    for payload in payloads:
        res = await async_client.post("/transactions/", json=payload)
        assert res.status_code == 201

    response = await async_client.get("/transactions/")
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3

    for tx in transactions:
        assert all(k in tx for k in ["uid", "type", "amount", "description", "date"])


@pytest.mark.asyncio
async def test_get_transaction_by_uid(async_client):
    """Test retrieving a single transaction by UID."""
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    assert create_res.status_code == 201
    created_tx = create_res.json()

    res = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert res.status_code == 200
    data = res.json()
    assert data["uid"] == created_tx["uid"]
    assert data["amount"] == created_tx["amount"]
    assert data["type"] == created_tx["type"]
    assert data["description"] == created_tx["description"]


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(async_client):
    fake_uid = f"tx-{uuid.uuid4()}"
    res = await async_client.get(f"/transactions/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_transaction(async_client, test_db):
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    assert create_res.status_code == 201
    created_tx = create_res.json()

    update_payload = {"description": "Updated transaction", "amount": 999.99}
    res = await async_client.patch(f"/transactions/{created_tx['uid']}", json=update_payload)
    assert res.status_code == 200
    
    updated = res.json()
    assert updated["description"] == "Updated transaction"
    assert updated["amount"] == 999.99

    db_tx = await test_db.transactions.find_one({"uid": created_tx["uid"]})
    assert db_tx["description"] == "Updated transaction"
    assert db_tx["amount"] == 999.99


@pytest.mark.asyncio
async def test_update_nonexistent_transaction(async_client):
    fake_uid = f"tx-{uuid.uuid4()}"
    res = await async_client.patch(f"/transactions/{fake_uid}", json={"description": "fail"})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_transaction(async_client, test_db):
    payload = random_transaction()
    create_res = await async_client.post("/transactions/", json=payload)
    created_tx = create_res.json()

    res = await async_client.delete(f"/transactions/{created_tx['uid']}")
    assert res.status_code == 200
    assert res.json()["status"] == "deleted"

    get_res = await async_client.get(f"/transactions/{created_tx['uid']}")
    assert get_res.status_code == 404

    db_tx = await test_db.transactions.find_one({"uid": created_tx["uid"]})
    assert db_tx is None


@pytest.mark.asyncio
async def test_delete_nonexistent_transaction(async_client):
    fake_uid = f"tx-{uuid.uuid4()}"
    res = await async_client.delete(f"/transactions/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_transaction_validation(async_client):
    """Test validation for invalid or incomplete data."""
    invalid_payload = random_transaction()
    invalid_payload["type"] = "invalid_type"
    res = await async_client.post("/transactions/", json=invalid_payload)
    assert res.status_code == 422

    incomplete_payload = {"description": "Missing fields"}
    res = await async_client.post("/transactions/", json=incomplete_payload)
    assert res.status_code == 422

    invalid_amount = random_transaction()
    invalid_amount["amount"] = -100
    res = await async_client.post("/transactions/", json=invalid_amount)
    assert res.status_code == 422

    income_missing_account = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 100,
        "description": "Income without account",
        "date": random_date(),
        "type": "income",
    }
    res = await async_client.post("/transactions/", json=income_missing_account)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_transaction_types(async_client):
    """Test all transaction types can be created."""
    income = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 1000,
        "description": "Salary",
        "date": random_date(),
        "type": "income",
        "account_uid": "acct-checking",
        "category_uid": "cat-salary",
    }
    expense = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 50,
        "description": "Groceries",
        "date": random_date(),
        "type": "expense",
        "account_uid": "acct-checking",
        "category_uid": "cat-food",
    }
    transfer = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 200,
        "description": "Transfer to savings",
        "date": random_date(),
        "type": "transfer",
        "from_account_uid": "acct-checking",
        "to_account_uid": "acct-savings",
    }
    reimburse = {
        "uid": f"tx-{uuid.uuid4()}",
        "amount": 75,
        "description": "Reimbursement",
        "date": random_date(),
        "type": "reimburse",
        "account_uid": "acct-checking",
        "expense_uid": "tx-expense-001",
    }

    for tx in [income, expense, transfer, reimburse]:
        res = await async_client.post("/transactions/", json=tx)
        assert res.status_code == 201, f"{tx['type']} transaction creation failed"

    res = await async_client.get("/transactions/")
    assert res.status_code == 200
    assert len(res.json()) == 4


# ---------- 🧩 NEW TEST: Reimbursement Details ----------

@pytest.mark.asyncio
async def test_reimburse_transaction_includes_reimbursed_details(async_client, test_db):
    """Ensure reimbursement returns enriched reimbursed transaction details."""

    # Create linked account/category
    await test_db["accounts"].insert_one({"uid": "acct-reimburse", "name": "BPI Checking"})
    await test_db["categories"].insert_one({"uid": "cat-medical", "name": "Medical"})

    # 1️⃣ Create the expense transaction
    expense_payload = {
        "type": "expense",
        "amount": 1200,
        "account_uid": "acct-reimburse",
        "category_uid": "cat-medical",
        "description": "Vet bill",
        "date": datetime.now().isoformat(),
    }
    exp_res = await async_client.post("/transactions/", json=expense_payload)
    assert exp_res.status_code == 201
    expense_uid = exp_res.json()["uid"]

    # 2️⃣ Create reimbursement referencing that expense
    reimburse_payload = {
        "type": "reimburse",
        "amount": 1200,
        "account_uid": "acct-reimburse",
        "expense_uid": expense_uid,
        "description": "Refund from clinic",
        "date": datetime.now().isoformat(),
    }
    res = await async_client.post("/transactions/", json=reimburse_payload)
    assert res.status_code == 201, f"Reimburse create failed: {res.text}"

    data = res.json()
    assert "reimbursed_transaction" in data, "Expected reimbursed_transaction in response"
    reimbursed = data["reimbursed_transaction"]

    # Base checks
    assert reimbursed["uid"] == expense_uid
    assert reimbursed["type"] == "expense"
    assert reimbursed["amount"] == 1200
    assert reimbursed["account_name"] == "BPI Checking"
    assert reimbursed["category_name"] == "Medical"

    # 3️⃣ GET /transactions/{uid} should still include enrichment
    get_res = await async_client.get(f"/transactions/{data['uid']}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["reimbursed_transaction"]["account_name"] == "BPI Checking"
    assert get_data["reimbursed_transaction"]["category_name"] == "Medical"
