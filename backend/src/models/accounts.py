from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase

class AccountModel:
    collection_name = "accounts"

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
        
        # Set default values for interest fields if not provided
        data.setdefault("interest_rate", 0)
        data.setdefault("interest_frequency", "monthly")
        data.setdefault("description", None)
        
        return data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new account"""
        data = self.prepare_data(data)
        result = await self.collection.insert_one(data)
        new_account = await self.collection.find_one({"_id": result.inserted_id})
        return new_account
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all accounts."""
        cursor = self.collection.find().sort("created_at", -1)
        return await cursor.to_list(length=1000)
    
    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get an account by UID"""
        return await self.collection.find_one({"uid": uid})
    
    async def update(self, uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an account"""
        data["updated_at"] = datetime.now()
        result = await self.collection.update_one({"uid": uid}, {"$set": data})
        if result.modified_count:
            return await self.get_by_uid(uid)
        return None
    
    async def delete(self, uid: str) -> bool:
        """Delete an account"""
        result = await self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0
    
    async def calculate_interest(self, uid: str) -> Optional[float]:
        """Calculate monthly interest for an account"""
        account = await self.get_by_uid(uid)
        if not account or not account.get("interest_rate"):
            return 0
        
        balance = account.get("balance", 0)
        annual_rate = account.get("interest_rate", 0)
        frequency = account.get("interest_frequency", "monthly")
        
        # Calculate interest based on frequency
        if frequency == "monthly":
            interest = balance * (annual_rate / 100) / 12
        elif frequency == "quarterly":
            interest = balance * (annual_rate / 100) / 4
        elif frequency == "annually":
            interest = balance * (annual_rate / 100)
        else:
            interest = balance * (annual_rate / 100) / 12  # default to monthly
        
        return round(interest, 2)
    
    @classmethod
    async def ensure_indexes(cls, db: AsyncIOMotorDatabase) -> None:
        """Ensure indexes for the accounts collection."""
        collection = db[cls.collection_name]
        await collection.create_index("uid", unique=True)
        await collection.create_index("created_at")
        await collection.create_index("updated_at")
        await collection.create_index("type")
        await collection.create_index("balance")

        print("✅ AccountModel indexes ensured")