# src/db_indexes.py
from src.database import get_db

async def create_indexes():
    db = await get_db()
    if db is None:
        raise RuntimeError("MongoDB connection not initialized before creating indexes.")

    await db.transactions.create_index("uid", unique=True)
    print("✅ Indexes created for 'transactions'")


async def create_indexes():
    db = await get_db()
    if db is None:
        raise RuntimeError("Database is not connected before index creation")

    await db.transactions.create_index("uid", unique=True)
    await db.transactions.create_index("type")
    await db.transactions.create_index("date")
    await db.transactions.create_index("account_uid")
    await db.transactions.create_index("category_uid")

    print("✅ MongoDB indexes created")
