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

    payloads = [random_category() for _ in range(3)]
    created_uids = []
    
    for payload in payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        created_uids.append(res.json()["uid"])

    response = await async_client.get("/categories/")
    categories = response.json()
    assert len(categories) >= 3

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
    incomplete_payload = {"name": "No type or budget"}
    res = await async_client.post("/categories/", json=incomplete_payload)
    assert res.status_code == 422

    negative_payload = random_category()
    negative_payload["budgeted_amount"] = -100
    res = await async_client.post("/categories/", json=negative_payload)
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_hierarchical_categories(async_client, test_db):
    """Test creating parent and child categories and retrieving the hierarchy."""
    parent_payload = random_category()
    parent_payload["name"] = "Parent Category"
    parent_res = await async_client.post("/categories/", json=parent_payload)
    assert parent_res.status_code == 201
    parent_cat = parent_res.json()
    
    child_payloads = [random_category(parent_uid=parent_cat["uid"]) for _ in range(3)]
    child_cats = []
    for payload in child_payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        child_cats.append(res.json())
    
    get_res = await async_client.get(f"/categories/{parent_cat['uid']}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["parent_uid"] is None
    children_uids = [child["uid"] for child in child_cats]
    assert "children" in data
    returned_child_uids = [child["uid"] for child in data["children"]]
    for uid in children_uids:
        assert uid in returned_child_uids
    for child in data["children"]:
        assert child["parent_uid"] == parent_cat["uid"]

@pytest.mark.asyncio
async def test_multi_level_category_tree(async_client, test_db):
    """Test creating a multi-level category tree and retrieving it."""
    parent_payload = random_category()
    parent_payload["name"] = "Parent Category"
    parent_res = await async_client.post("/categories/", json=parent_payload)
    assert parent_res.status_code == 201
    parent_cat = parent_res.json()
    
    child_payloads = [random_category(parent_uid=parent_cat["uid"]) for _ in range(2)]
    child_cats = []
    for payload in child_payloads:
        res = await async_client.post("/categories/", json=payload)
        assert res.status_code == 201
        child_cats.append(res.json())
    
    grandchild_cats = []
    for child in child_cats:
        grandchild_payloads = [random_category(parent_uid=child["uid"]) for _ in range(2)]
        for payload in grandchild_payloads:
            res = await async_client.post("/categories/", json=payload)
            assert res.status_code == 201
            grandchild_cats.append(res.json())
    
    get_res = await async_client.get(f"/categories/{parent_cat['uid']}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["parent_uid"] is None
    assert "children" in data
    retrieved_child_uids = [child["uid"] for child in data["children"]]
    for child in child_cats:
        assert child["uid"] in retrieved_child_uids
        child_data = next(c for c in data["children"] if c["uid"] == child["uid"])
        assert "children" in child_data
        grandchild_uids_for_child = [gc["uid"] for gc in grandchild_cats if gc["parent_uid"] == child["uid"]]
        retrieved_grandchild_uids = [gc["uid"] for gc in child_data["children"]]
        for uid in grandchild_uids_for_child:
            assert uid in retrieved_grandchild_uids


# ---------- NEW TEST: Aggregated Tree Endpoint ----------

@pytest.mark.asyncio
async def test_category_tree_aggregation(async_client, test_db):
    """Test that /categories/tree aggregates totals, budgets, and flags over-budget categories."""

    await test_db.categories.delete_many({})

    categories = [
        {
            "uid": "cat-food",
            "name": "Food",
            "budget": 10000,
            "total_spent": 0,
            "total_earned": 0,
            "budget_used": 0,
            "parent_uid": None,
        },
        {
            "uid": "cat-dining",
            "name": "Dining Out",
            "budget": 6000,
            "total_spent": 8000,
            "total_earned": 0,
            "budget_used": 8000,
            "parent_uid": "cat-food",
        },
        {
            "uid": "cat-groceries",
            "name": "Groceries",
            "budget": 4000,
            "total_spent": 4000,
            "total_earned": 0,
            "budget_used": 4000,
            "parent_uid": "cat-food",
        },
    ]
    await test_db.categories.insert_many(categories)

    response = await async_client.get("/categories/tree")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    root = data[0]
    children = root["children"]
    assert root["uid"] == "cat-food"
    assert len(children) == 2

    assert root["total_spent"] == 12000
    assert root["budget_used"] == 12000
    assert root["budget_utilization"] == round(12000 / 10000, 4)
    assert root["is_over_budget"] is True

    for child in children:
        if child["uid"] == "cat-dining":
            assert child["is_over_budget"] is True
            assert child["budget_utilization"] == round(8000 / 6000, 4)
        elif child["uid"] == "cat-groceries":
            assert child["is_over_budget"] is False
            assert child["budget_utilization"] == round(4000 / 4000, 4)

        assert "total_spent" in child
        assert "budget_utilization" in child
        assert "is_over_budget" in child
        assert isinstance(child["children"], list)
