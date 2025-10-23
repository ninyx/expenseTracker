from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException


class CategoryModel:
    collection_name = "categories"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.collection_name]

    # =====================================================
    # ============= BASIC CRUD OPERATIONS =================
    # =====================================================

    @staticmethod
    def prepare_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for database insertion."""
        if "uid" not in data:
            data["uid"] = str(uuid4())
        if "created_at" not in data:
            data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()

        # initialize hierarchy and budget fields
        data.setdefault("parent_uid", None)
        data.setdefault("total_spent", 0)
        data.setdefault("total_earned", 0)
        data.setdefault("budget", 0)
        data.setdefault("budget_used", 0)
        return data
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new category.
        - Checks if parent exists (if parent_uid provided)
        - Ensures total child budgets do not exceed parent's budget
        """
        data = self.prepare_data(data)
        parent_uid = data.get("parent_uid")

        # ✅ Validate parent if this is a subcategory
        if parent_uid:
            parent = await self.get_by_uid(parent_uid)
            if not parent:
                raise HTTPException(
                    status_code=404,
                    detail=f"Parent category with UID '{parent_uid}' not found."
                )

            parent_budget = parent.get("budget", 0)
            if parent_budget <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Parent category '{parent.get('name')}' has no budget set."
                )

            # Get existing children
            children = await self.get_children(parent_uid)
            total_child_budget = sum(child.get("budget", 0) for child in children)

            # Include this new child's proposed budget
            new_total = total_child_budget + data.get("budget", 0)

            # ✅ Overflow detection
            if new_total > parent_budget:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Budget overflow: total child budgets ({new_total}) "
                        f"would exceed parent budget ({parent_budget})."
                    ),
                )

        # ✅ Proceed with insertion
        result = await self.collection.insert_one(data)
        new_category = await self.collection.find_one({"_id": result.inserted_id})
        return new_category


    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all categories."""
        cursor = self.collection.find().sort("created_at", -1)
        return await cursor.to_list(length=1000)

    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a category by UID"""
        return await self.collection.find_one({"uid": uid})

    async def update(self, uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a category"""
        data["updated_at"] = datetime.now()
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

    # =====================================================
    # =============== HIERARCHY HELPERS ===================
    # =====================================================

    async def get_children(self, parent_uid: str) -> List[Dict[str, Any]]:
        """Return all direct children of a parent category."""
        cursor = self.collection.find({"parent_uid": parent_uid})
        return [child async for child in cursor]

    async def get_parent(self, uid: str) -> Optional[Dict[str, Any]]:
        """Return parent category if it exists."""
        cat = await self.get_by_uid(uid)
        if cat and cat.get("parent_uid"):
            return await self.get_by_uid(cat["parent_uid"])
        return None
