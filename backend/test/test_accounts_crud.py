# tests/test_accounts_crud.py
import pytest
import random
import uuid

# ---------- Utility functions ----------

ACCOUNT_TYPES = [
    "cash", "checking", "savings", "credit card", "loan",
    "mortgage", "investment", "retirement", "digital wallet"
]

def random_account() -> dict:
    """Generate dummy account data conforming to our schema."""
    account_type = random.choice(ACCOUNT_TYPES)
    uid = f"acct-{uuid.uuid4()}"
    return {
        "uid": uid,
        "name": f"Test {account_type.capitalize()} Account",
        "type": account_type,
        "balance": round(random.uniform(1000, 10000), 2),
        "notes": f"Test note for {account_type} account"
    }

# ---------- CRUD Tests ----------

@pytest.mark.asyncio
async def test_create_account(async_client, test_db):
    """Test creating a new account."""
    payload = random_account()
    response = await async_client.post("/accounts/", json=payload)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["type"] == payload["type"]
    assert data["balance"] == payload["balance"]
    assert "uid" in data
    
    # Verify it was saved to the database
    saved_acct = await test_db.accounts.find_one({"uid": data["uid"]})
    assert saved_acct is not None
    assert saved_acct["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_accounts(async_client, test_db):
    """Test retrieving all accounts."""
    response = await async_client.get("/accounts/")
    assert response.status_code == 200
    accounts = response.json()
    assert isinstance(accounts, list)

    # Create 3 accounts
    payloads = [random_account() for _ in range(3)]
    created_uids = []
    
    for payload in payloads:
        res = await async_client.post("/accounts/", json=payload)
        assert res.status_code == 201
        created_uids.append(res.json()["uid"])

    # Retrieve all accounts
    response = await async_client.get("/accounts/")
    accounts = response.json()
    assert len(accounts) >= 3, f"Expected at least 3 accounts, got {len(accounts)}"

    # Verify all created UIDs are present
    retrieved_uids = [acct["uid"] for acct in accounts]
    for uid in created_uids:
        assert uid in retrieved_uids


@pytest.mark.asyncio
async def test_get_account_by_uid(async_client, test_db):
    """Test retrieving a single account by UID."""
    payload = random_account()
    create_res = await async_client.post("/accounts/", json=payload)
    created_acct = create_res.json()

    res = await async_client.get(f"/accounts/{created_acct['uid']}")
    assert res.status_code == 200
    data = res.json()
    assert data["uid"] == created_acct["uid"]
    assert data["name"] == created_acct["name"]
    assert data["type"] == created_acct["type"]


@pytest.mark.asyncio
async def test_get_nonexistent_account(async_client, test_db):
    """Test retrieving an account that doesn't exist."""
    fake_uid = f"acct-{uuid.uuid4()}"
    res = await async_client.get(f"/accounts/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_account(async_client, test_db):
    """Test updating an existing account."""
    payload = random_account()
    create_res = await async_client.post("/accounts/", json=payload)
    created_acct = create_res.json()

    update_payload = {
        "name": "Updated Account Name",
        "balance": 5555.55
    }

    res = await async_client.patch(f"/accounts/{created_acct['uid']}", json=update_payload)
    assert res.status_code == 200

    updated = res.json()
    assert updated["name"] == update_payload["name"]
    assert updated["balance"] == update_payload["balance"]
    assert updated["uid"] == created_acct["uid"]  # unchanged

    # Verify update in database
    db_acct = await test_db.accounts.find_one({"uid": created_acct["uid"]})
    assert db_acct["name"] == update_payload["name"]
    assert db_acct["balance"] == update_payload["balance"]


@pytest.mark.asyncio
async def test_update_nonexistent_account(async_client, test_db):
    """Test updating an account that doesn't exist."""
    fake_uid = f"acct-{uuid.uuid4()}"
    update_payload = {"name": "This should fail"}
    res = await async_client.patch(f"/accounts/{fake_uid}", json=update_payload)
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_account(async_client, test_db):
    """Test deleting an account."""
    payload = random_account()
    create_res = await async_client.post("/accounts/", json=payload)
    created_acct = create_res.json()

    res = await async_client.delete(f"/accounts/{created_acct['uid']}")
    assert res.status_code == 200
    delete_data = res.json()
    assert delete_data["status"] == "deleted"
    assert delete_data["uid"] == created_acct["uid"]

    # Verify deletion from database
    db_acct = await test_db.accounts.find_one({"uid": created_acct["uid"]})
    assert db_acct is None


@pytest.mark.asyncio
async def test_delete_nonexistent_account(async_client, test_db):
    """Test deleting an account that doesn't exist."""
    fake_uid = f"acct-{uuid.uuid4()}"
    res = await async_client.delete(f"/accounts/{fake_uid}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_account_validation(async_client, test_db):
    """Test account validation for invalid data."""
    # Invalid type
    invalid_payload = random_account()
    invalid_payload["type"] = "invalid_type"
    res = await async_client.post("/accounts/", json=invalid_payload)
    assert res.status_code == 422

    # Missing required fields
    incomplete_payload = {"name": "No type or balance"}
    res = await async_client.post("/accounts/", json=incomplete_payload)
    assert res.status_code == 422

    # Negative balance
    negative_balance = random_account()
    negative_balance["balance"] = -100
    res = await async_client.post("/accounts/", json=negative_balance)
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_all_account_types(async_client, test_db):
    """Test that all valid account types can be created."""
    ACCOUNT_TYPES = [
        "cash", "checking", "savings", "credit card", "loan",
        "mortgage", "investment", "retirement", "digital wallet"
    ]
    
    created_uids = []
    
    for acc_type in ACCOUNT_TYPES:
        payload = {
            "uid": f"acct-{uuid.uuid4()}",
            "name": f"Test {acc_type.capitalize()} Account",
            "type": acc_type,
            "balance": round(random.uniform(1000, 10000), 2),
            "notes": f"Test note for {acc_type} account"
        }
        res = await async_client.post("/accounts/", json=payload)
        assert res.status_code == 201, f"Failed to create account type {acc_type}"
        created_uids.append(res.json()["uid"])
    
    # Verify all accounts exist in the API
    response = await async_client.get("/accounts/")
    assert response.status_code == 200
    accounts = response.json()
    retrieved_uids = [acct["uid"] for acct in accounts]
    
    for uid in created_uids:
        assert uid in retrieved_uids, f"Account UID {uid} not found in retrieved accounts"
