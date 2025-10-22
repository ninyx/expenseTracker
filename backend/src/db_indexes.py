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

    print("✅ MongoDB indexes created")
