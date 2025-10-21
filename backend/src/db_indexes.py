# src/db_indexes.py
from src import database as db

async def create_indexes():
    if db.db is None:
        raise RuntimeError("MongoDB connection not initialized before creating indexes.")

    await db.db.transactions.create_index("uid", unique=True)
    print("✅ Indexes created for 'transactions'")


async def create_indexes():
    if db.db is None:
        raise RuntimeError("Database is not connected before index creation")

    await db.db.transactions.create_index("uid", unique=True)
    await db.db.transactions.create_index("type")
    await db.db.transactions.create_index("date")
    await db.db.transactions.create_index("account_uid")
    await db.db.transactions.create_index("category_uid")

    print("✅ MongoDB indexes created")
