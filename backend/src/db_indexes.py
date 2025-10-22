# src/db_indexes.py
from src.database import get_db
from pymongo import IndexModel, ASCENDING

async def create_indexes():
    """Create MongoDB indexes for all collections"""
    db = await get_db()
    if db is None:
        raise RuntimeError("Database is not connected before index creation")

    # Transaction indexes
    transaction_indexes = [
        IndexModel([("uid", ASCENDING)], unique=True),
        IndexModel([("type", ASCENDING)]),
        IndexModel([("date", ASCENDING)]),
        IndexModel([("account_uid", ASCENDING)]),
        IndexModel([("category_uid", ASCENDING)])
    ]
    await db.transactions.create_indexes(transaction_indexes)

    # Account indexes
    account_indexes = [
        IndexModel([("uid", ASCENDING)], unique=True),
        IndexModel([("type", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
        IndexModel([("updated_at", ASCENDING)])
    ]

    await db.accounts.create_indexes(account_indexes)

    print("✅ MongoDB indexes created")

    # Category indexes
    category_indexes = [
        IndexModel([("uid", ASCENDING)], unique=True),
        IndexModel([("name", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
        IndexModel([("updated_at", ASCENDING)])
    ]

    await db.categories.create_indexes(category_indexes)
    print("✅ MongoDB indexes created for categories")