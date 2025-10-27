from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase


class CreditModel:
    collection_name = "credits"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[self.collection_name]
        self.payments_collection = db["credit_payments"]
        self.charges_collection = db["credit_charges"]

    @staticmethod
    def prepare_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for database insertion."""
        if "uid" not in data:
            data["uid"] = str(uuid4())
        if "created_at" not in data:
            data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()
        
        # Calculate available credit
        if "credit_limit" in data and "current_balance" in data:
            data["available_credit"] = data["credit_limit"] - data["current_balance"]
        
        return data

    # =====================================================
    # ============= CRUD OPERATIONS =======================
    # =====================================================

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new credit obligation"""
        data = self.prepare_data(data)
        result = await self.collection.insert_one(data)
        new_credit = await self.collection.find_one({"_id": result.inserted_id})
        return new_credit

    async def get_all(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all credit obligations"""
        query = {"is_active": True} if active_only else {}
        cursor = self.collection.find(query).sort("created_at", -1)
        return await cursor.to_list(length=1000)

    async def get_by_uid(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get a credit obligation by UID"""
        credit = await self.collection.find_one({"uid": uid})
        if credit:
            # Add computed fields
            credit = await self._enrich_credit_data(credit)
        return credit

    async def update(self, uid: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a credit obligation"""
        data["updated_at"] = datetime.now()
        
        # Recalculate available credit if balance or limit changed
        if "credit_limit" in data or "current_balance" in data:
            existing = await self.collection.find_one({"uid": uid})
            credit_limit = data.get("credit_limit", existing.get("credit_limit", 0))
            current_balance = data.get("current_balance", existing.get("current_balance", 0))
            data["available_credit"] = credit_limit - current_balance
        
        result = await self.collection.update_one({"uid": uid}, {"$set": data})
        if result.modified_count:
            return await self.get_by_uid(uid)
        return None

    async def delete(self, uid: str) -> bool:
        """Delete a credit obligation"""
        result = await self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0

    # =====================================================
    # ============= PAYMENT OPERATIONS ====================
    # =====================================================

    async def record_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a payment on credit"""
        credit_uid = payment_data["credit_uid"]
        amount = payment_data["amount"]
        
        # Get current credit
        credit = await self.collection.find_one({"uid": credit_uid})
        if not credit:
            raise ValueError(f"Credit with UID {credit_uid} not found")
        
        # Update balance
        new_balance = max(0, credit["current_balance"] - amount)
        await self.update(credit_uid, {"current_balance": new_balance})
        
        # Record payment history
        payment_data["uid"] = str(uuid4())
        payment_data["created_at"] = datetime.now()
        result = await self.payments_collection.insert_one(payment_data)
        
        return await self.payments_collection.find_one({"_id": result.inserted_id})

    async def record_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record a new charge/purchase on credit"""
        credit_uid = charge_data["credit_uid"]
        amount = charge_data["amount"]
        
        # Get current credit
        credit = await self.collection.find_one({"uid": credit_uid})
        if not credit:
            raise ValueError(f"Credit with UID {credit_uid} not found")
        
        # Check if charge exceeds credit limit
        new_balance = credit["current_balance"] + amount
        if new_balance > credit["credit_limit"]:
            raise ValueError(
                f"Charge of ₱{amount:,.2f} would exceed credit limit. "
                f"Available: ₱{credit['available_credit']:,.2f}"
            )
        
        # Update balance
        await self.update(credit_uid, {"current_balance": new_balance})
        
        # Record charge history
        charge_data["uid"] = str(uuid4())
        charge_data["created_at"] = datetime.now()
        result = await self.charges_collection.insert_one(charge_data)
        
        return await self.charges_collection.find_one({"_id": result.inserted_id})

    async def get_payment_history(self, credit_uid: str) -> List[Dict[str, Any]]:
        """Get payment history for a credit"""
        cursor = self.payments_collection.find(
            {"credit_uid": credit_uid}
        ).sort("payment_date", -1)
        return await cursor.to_list(length=1000)

    async def get_charge_history(self, credit_uid: str) -> List[Dict[str, Any]]:
        """Get charge history for a credit"""
        cursor = self.charges_collection.find(
            {"credit_uid": credit_uid}
        ).sort("charge_date", -1)
        return await cursor.to_list(length=1000)

    # =====================================================
    # ============= ANALYTICS & REPORTING =================
    # =====================================================

    async def get_summary(self) -> Dict[str, Any]:
        """Get overall credit summary"""
        credits = await self.get_all(active_only=True)
        
        total_limit = sum(c.get("credit_limit", 0) for c in credits)
        total_balance = sum(c.get("current_balance", 0) for c in credits)
        total_available = sum(c.get("available_credit", 0) for c in credits)
        
        # Calculate utilization rate
        utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        
        # Count overdue
        today = date.today()
        overdue_count = 0
        for credit in credits:
            if credit.get("due_date") and credit["current_balance"] > 0:
                # Check if due date has passed this month
                due_this_month = date(today.year, today.month, credit["due_date"])
                if today > due_this_month:
                    overdue_count += 1
        
        return {
            "total_credit_limit": total_limit,
            "total_balance": total_balance,
            "total_available": total_available,
            "overall_utilization": round(utilization, 2),
            "active_credits": len(credits),
            "overdue_count": overdue_count,
        }

    async def get_upcoming_due_dates(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get credits with upcoming due dates"""
        credits = await self.get_all(active_only=True)
        today = date.today()
        
        upcoming = []
        for credit in credits:
            if credit.get("due_date") and credit["current_balance"] > 0:
                # Calculate next due date
                due_day = credit["due_date"]
                if due_day <= today.day:
                    # Due date is next month
                    next_month = today.month + 1 if today.month < 12 else 1
                    next_year = today.year if today.month < 12 else today.year + 1
                    next_due = date(next_year, next_month, due_day)
                else:
                    # Due date is this month
                    next_due = date(today.year, today.month, due_day)
                
                days_until = (next_due - today).days
                
                if 0 <= days_until <= days:
                    upcoming.append({
                        **credit,
                        "next_due_date": next_due,
                        "days_until_due": days_until,
                    })
        
        return sorted(upcoming, key=lambda x: x["days_until_due"])

    async def _enrich_credit_data(self, credit: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed fields to credit data"""
        # Utilization rate
        if credit["credit_limit"] > 0:
            credit["utilization_rate"] = round(
                (credit["current_balance"] / credit["credit_limit"]) * 100, 2
            )
        else:
            credit["utilization_rate"] = 0
        
        # Days until due
        if credit.get("due_date") and credit["current_balance"] > 0:
            today = date.today()
            due_day = credit["due_date"]
            
            if due_day <= today.day:
                # Due date is next month
                next_month = today.month + 1 if today.month < 12 else 1
                next_year = today.year if today.month < 12 else today.year + 1
                next_due = date(next_year, next_month, due_day)
            else:
                # Due date is this month
                next_due = date(today.year, today.month, due_day)
            
            credit["days_until_due"] = (next_due - today).days
            credit["is_overdue"] = today > next_due
        else:
            credit["days_until_due"] = None
            credit["is_overdue"] = False
        
        return credit

    @classmethod
    async def ensure_indexes(cls, db: AsyncIOMotorDatabase) -> None:
        """Ensure indexes for the credits collection."""
        collection = db[cls.collection_name]
        await collection.create_index("uid", unique=True)
        await collection.create_index("created_at")
        await collection.create_index("is_active")
        await collection.create_index("due_date")