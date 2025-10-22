# tests/test_categories_crud.py
import pytest
import random
import uuid

# ---------- Utility functions ----------

CATEGORY_NAMES = [
    "Food", "Transportation", "Entertainment", "Salary", "Shopping",
    "Utilities", "Health", "Education"
]

TRANSACTION_TYPES = ["income", "expense"]

def random_category(parent_uid=None) -> dict:
    """Generate dummy category data conforming to our schema."""
    uid = f"cat-{uuid.uuid4()}"
    name = f"{random.choice(CATEGORY_NAMES)} {random.choice(TRANSACTION_TYPES).capitalize()}"
    return {
        "uid": uid,
        "name": name,
        "description": f"Test description for {name}",
        "transaction_type": random.choice(TRANSACTION_TYPES),
        "budgeted_amount": round(random.uniform(100, 2000), 2),
        "frequency": random.choice(["monthly", "weekly", "yearly", "one-time"]),
        "parent_uid": parent_uid,
        "is_active": True
    }

# ---------- CRUD Tests ----------

@pytest.mark.asyncio
async def test_create_category(async_client, test_db):
    """Test creating a new category."""
    payload = random_category()
    response = await async_client.post("/categories/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["transaction_type"] == payload["transaction_type"]
    assert "uid" in data
    
    # Verify it was saved to the database
    saved_cat = await test_db.categories.find_one({"uid": data["uid"]})
    assert saved_cat is not None
    assert saved_cat["name"] == payload["name"]

@pytest.mark.asyncio
async def test_get_categories(async_client, test_db):
    """Test retrieving all categories."""
    response = await async_client.get("/categories/")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)

    # Create 3 categories
    payloads = [random_category() for _ in range(3)]
    created_uids = []
    
    for payload in payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        created_uids.append(res.json()["uid"])

    # Retrieve all categories
    response = await async_client.get("/categories/")
    categories = response.json()
    assert len(categories) >= 3

    # Verify all created UIDs are present
    retrieved_uids = [cat["uid"] for cat in categories]
    for uid in created_uids:
        assert uid in retrieved_uids

@pytest.mark.asyncio
async def test_get_category_by_uid(async_client, test_db):
    """Test retrieving a single category by UID."""
    payload = random_category()
    create_res = await async_client.post("/categories/", json=payload)
    created_cat = create_res.json()

    res = await async_client.get(f"/categories/{created_cat['uid']}")
    assert res.status_code == 200
    data = res.json()
    assert data["uid"] == created_cat["uid"]
    assert data["name"] == created_cat["name"]

@pytest.mark.asyncio
async def test_get_nonexistent_category(async_client, test_db):
    """Test retrieving a category that doesn't exist."""
    fake_uid = f"cat-{uuid.uuid4()}"
    res = await async_client.get(f"/categories/{fake_uid}")
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_update_category(async_client, test_db):
    """Test updating an existing category."""
    payload = random_category()
    create_res = await async_client.post("/categories/", json=payload)
    created_cat = create_res.json()

    update_payload = {
        "name": "Updated Category Name",
        "budgeted_amount": 999.99
    }

    res = await async_client.patch(f"/categories/{created_cat['uid']}", json=update_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == update_payload["name"]
    assert updated["budgeted_amount"] == update_payload["budgeted_amount"]

    # Verify update in database
    db_cat = await test_db.categories.find_one({"uid": created_cat["uid"]})
    assert db_cat["name"] == update_payload["name"]
    assert db_cat["budgeted_amount"] == update_payload["budgeted_amount"]

@pytest.mark.asyncio
async def test_update_nonexistent_category(async_client, test_db):
    """Test updating a category that doesn't exist."""
    fake_uid = f"cat-{uuid.uuid4()}"
    update_payload = {"name": "This should fail"}
    res = await async_client.patch(f"/categories/{fake_uid}", json=update_payload)
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_delete_category(async_client, test_db):
    """Test deleting a category."""
    payload = random_category()
    create_res = await async_client.post("/categories/", json=payload)
    created_cat = create_res.json()

    res = await async_client.delete(f"/categories/{created_cat['uid']}")
    assert res.status_code == 200
    delete_data = res.json()
    assert delete_data["status"] == "deleted"
    assert delete_data["uid"] == created_cat["uid"]

    # Verify deletion from database
    db_cat = await test_db.categories.find_one({"uid": created_cat["uid"]})
    assert db_cat is None

@pytest.mark.asyncio
async def test_delete_nonexistent_category(async_client, test_db):
    """Test deleting a category that doesn't exist."""
    fake_uid = f"cat-{uuid.uuid4()}"
    res = await async_client.delete(f"/categories/{fake_uid}")
    assert res.status_code == 404

@pytest.mark.asyncio
async def test_category_validation(async_client, test_db):
    """Test category validation for invalid data."""
    # Missing required fields
    incomplete_payload = {"name": "No type or budget"}
    res = await async_client.post("/categories/", json=incomplete_payload)
    assert res.status_code == 422

    # Negative budgeted amount
    negative_payload = random_category()
    negative_payload["budgeted_amount"] = -100
    res = await async_client.post("/categories/", json=negative_payload)
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_hierarchical_categories(async_client, test_db):
    """Test creating parent and child categories and retrieving the hierarchy."""
    
    # 1️⃣ Create a parent category
    parent_payload = random_category()
    parent_payload["name"] = "Parent Category"
    parent_res = await async_client.post("/categories/", json=parent_payload)
    assert parent_res.status_code == 201
    parent_cat = parent_res.json()
    
    # 2️⃣ Create child categories
    child_payloads = [
        random_category(parent_uid=parent_cat["uid"]) for _ in range(3)
    ]
    child_cats = []
    for payload in child_payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        child_cats.append(res.json())
    
    # 3️⃣ Retrieve the parent category
    get_res = await async_client.get(f"/categories/{parent_cat['uid']}")
    assert get_res.status_code == 200
    data = get_res.json()
    
    # 4️⃣ Verify the parent UID is None (top-level)
    assert data["parent_uid"] is None
    
    # 5️⃣ Verify the children are returned
    children_uids = [child["uid"] for child in child_cats]
    
    # Assuming your API returns a `children` list in the response
    assert "children" in data
    returned_child_uids = [child["uid"] for child in data["children"]]
    
    for uid in children_uids:
        assert uid in returned_child_uids

    # 6️⃣ Optionally check that child category's parent_uid points to parent
    for child in data["children"]:
        assert child["parent_uid"] == parent_cat["uid"]


@pytest.mark.asyncio
async def test_multi_level_category_tree(async_client, test_db):
    """Test creating a multi-level category tree and retrieving it."""
    
    # 1️⃣ Create a top-level parent category
    parent_payload = random_category()
    parent_payload["name"] = "Parent Category"
    parent_res = await async_client.post("/categories/", json=parent_payload)
    assert parent_res.status_code == 201
    parent_cat = parent_res.json()
    
    # 2️⃣ Create child categories
    child_payloads = [
        random_category(parent_uid=parent_cat["uid"]) for _ in range(2)
    ]
    child_cats = []
    for payload in child_payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        child_cats.append(res.json())
    
    # 3️⃣ Create grandchildren for each child
    grandchild_cats = []
    for child in child_cats:
        grandchild_payloads = [
            random_category(parent_uid=child["uid"]) for _ in range(2)
        ]
        for payload in grandchild_payloads:
            res = await async_client.post("/categories/", json=payload)
            assert res.status_code == 201
            grandchild_cats.append(res.json())
    
    # 4️⃣ Retrieve the top-level parent category
    get_res = await async_client.get(f"/categories/{parent_cat['uid']}")
    assert get_res.status_code == 200
    data = get_res.json()
    
    # Verify parent_uid is None
    assert data["parent_uid"] is None
    
    # Verify the children
    assert "children" in data
    retrieved_child_uids = [child["uid"] for child in data["children"]]
    for child in child_cats:
        assert child["uid"] in retrieved_child_uids
        # Each child should have its own children (grandchildren)
        child_data = next(c for c in data["children"] if c["uid"] == child["uid"])
        assert "children" in child_data
        grandchild_uids_for_child = [gc["uid"] for gc in grandchild_cats if gc["parent_uid"] == child["uid"]]
        retrieved_grandchild_uids = [gc["uid"] for gc in child_data["children"]]
        for uid in grandchild_uids_for_child:
            assert uid in retrieved_grandchild_uids
