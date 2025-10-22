from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase

class CategoryModel:
    collection_name = "categories"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.collection_name]
    
    @staticmethod
    def prepare_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for database insertion."""
        if "uid" not in data:
            data["uid"] = str(uuid4())
        if "created_at" not in data:
            data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        return data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new category"""
        data = self.prepare_data(data)
        result = await self.collection.insert_one(data)
        new_category = await self.collection.find_one({"_id": result.inserted_id})
        return new_category
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        cursor = self.collection.find().sort("created_at", -1)
        return await cursor.to_list(length=1000)  # async Motor cursor
    
    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a category by UID"""
        return await self.collection.find_one({"uid": uid})
    
    async def update(self, uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a category"""
        data["updated_at"] = datetime.now()  # always update timestamp
        result = await self.collection.update_one({"uid": uid}, {"$set": data})
        if result.modified_count:
            return await self.get_by_uid(uid)
        return None
    
    async def delete(self, uid: str) -> bool:
        """Delete a category"""
        result = await self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0
    
    @classmethod
    async def ensure_indexes(cls, db: AsyncIOMotorDatabase) -> None:
        """Ensure indexes for the categories collection."""
        collection = db[cls.collection_name]
        await collection.create_index("uid", unique=True)
        await collection.create_index("created_at")
        await collection.create_index("updated_at")
        await collection.create_index("transaction_type")
        await collection.create_index("parent_uid")