# /src/models/transaction.py
"""Database model for transactions in MongoDB."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from src.schemas.transaction import TransactionCreate, TransactionResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

class TransactionModel:
    """Database operations for transactions in MongoDB."""
    collection_name = "transactions"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.collection_name]

    @staticmethod
    def prepare_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for database insertion."""
        if "uid" not in data:
            data["uid"] = str(uuid4())
        if "date" not in data:
            data["date"] = datetime.now()
        if "created_at" not in data:
            data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return data

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction"""
        data = self.prepare_data(data)
        result = await self.collection.insert_one(data)
        new_tx = await self.collection.find_one({"_id": result.inserted_id})
        return new_tx


    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all transactions."""
        cursor = self.collection.find().sort("date", -1)
        return await cursor.to_list(length=1000)  # async Motor cursor

    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a transaction by UID"""
        return await self.collection.find_one({"uid": uid})

    async def update(self, uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a transaction"""
        data["updated_at"] = datetime.now()  # always update timestamp
        result = await self.collection.update_one({"uid": uid}, {"$set": data})
        if result.modified_count:
            return await self.get_by_uid(uid)
        return None

    async def delete(self, uid: str) -> bool:
        """Delete a transaction"""
        result = await self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0

    @classmethod
    async def ensure_indexes(cls, db: AsyncIOMotorDatabase) -> None:
        """Ensure all required indexes exist"""
        await db[cls.collection_name].create_index("uid", unique=True)
        await db[cls.collection_name].create_index("type")
        await db[cls.collection_name].create_index("date")
        await db[cls.collection_name].create_index("account_uid")
        await db[cls.collection_name].create_index("category_uid")
        print("✅ Transaction indexes ensured")