from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime


class TransactionModel:
    """Handles CRUD operations and automatic balance/category/budget updates for transactions."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["transactions"]

    # ====================================================
    # =============== CRUD OPERATIONS =====================
    # ====================================================

    async def create(self, tx_data: dict):
        """Create a new transaction and update balances, category totals, and budgets."""
        tx_data["created_at"] = datetime.now()
        result = await self.collection.insert_one(tx_data)
        tx_data["_id"] = str(result.inserted_id)

        await self._update_account_balances_on_create(tx_data)
        await self._update_category_totals_on_create(tx_data)
        await self._update_budget_on_create(tx_data)
        return tx_data

    async def get_all(self):
        cursor = self.collection.find({})
        return [tx async for tx in cursor]

    async def get_by_uid(self, uid: str):
        return await self.collection.find_one({"uid": uid}, {"_id": 0})

    async def update(self, uid: str, update_data: dict):
        """Update an existing transaction and reapply all related logic."""
        existing = await self.collection.find_one({"uid": uid})
        if not existing:
            return None

        await self.collection.update_one({"uid": uid}, {"$set": update_data})
        updated = {**existing, **update_data}

        # Rollback → apply new effects
        await self._rollback_all(existing)
        await self._apply_all(updated)
        return updated

    async def delete(self, uid: str):
        """Delete a transaction and rollback all effects."""
        existing = await self.collection.find_one({"uid": uid})
        if not existing:
            return False

        await self.collection.delete_one({"uid": uid})
        await self._rollback_all(existing)
        return True

    # ====================================================
    # ============= LOGIC HELPERS ========================
    # ====================================================

    async def _apply_all(self, tx: dict):
        await self._update_account_balances_on_create(tx)
        await self._update_category_totals_on_create(tx)
        await self._update_budget_on_create(tx)

    async def _rollback_all(self, tx: dict):
        await self._rollback_account_balances(tx)
        await self._rollback_category_totals(tx)
        await self._rollback_budget(tx)

    # ====================================================
    # ============= ACCOUNT BALANCE LOGIC ================
    # ====================================================

    async def _update_account_balances_on_create(self, tx: dict):
        ttype = tx["type"]
        amt = tx["amount"]
        fee = tx.get("transfer_fee", 0) or 0

        if ttype == "income":
            await self.db["accounts"].update_one(
                {"uid": tx["account_uid"]}, {"$inc": {"balance": amt}}
            )
        elif ttype == "expense":
            await self.db["accounts"].update_one(
                {"uid": tx["account_uid"]}, {"$inc": {"balance": -amt}}
            )
        elif ttype == "reimburse":
            await self.db["accounts"].update_one(
                {"uid": tx["account_uid"]}, {"$inc": {"balance": amt}}
            )
        elif ttype == "transfer":
            await self.db["accounts"].update_one(
                {"uid": tx["from_account_uid"]}, {"$inc": {"balance": -(amt + fee)}}
            )
            await self.db["accounts"].update_one(
                {"uid": tx["to_account_uid"]}, {"$inc": {"balance": amt}}
            )

    async def _rollback_account_balances(self, tx: dict):
        """Reverse previous account effects."""
        ttype = tx["type"]
        amt = tx["amount"]
        fee = tx.get("transfer_fee", 0) or 0

        if ttype == "income":
            inc = -amt
        elif ttype == "expense":
            inc = amt
        elif ttype == "reimburse":
            inc = -amt
        elif ttype == "transfer":
            # Undo both directions
            await self.db["accounts"].update_one(
                {"uid": tx["from_account_uid"]}, {"$inc": {"balance": amt + fee}}
            )
            await self.db["accounts"].update_one(
                {"uid": tx["to_account_uid"]}, {"$inc": {"balance": -amt}}
            )
            return
        else:
            return

        await self.db["accounts"].update_one(
            {"uid": tx["account_uid"]}, {"$inc": {"balance": inc}}
        )

    # ====================================================
    # ============= CATEGORY TOTAL LOGIC =================
    # ====================================================

    async def _update_category_totals_on_create(self, tx: dict):
        ttype = tx["type"]
        amt = tx["amount"]
        category_uid = tx.get("category_uid")

        if not category_uid:
            return

        if ttype == "expense":
            await self.db["categories"].update_one(
                {"uid": category_uid}, {"$inc": {"total_spent": amt}}
            )
        elif ttype == "income":
            await self.db["categories"].update_one(
                {"uid": category_uid}, {"$inc": {"total_earned": amt}}
            )
        elif ttype == "reimburse":
            # reduce spending since reimbursed
            await self.db["categories"].update_one(
                {"uid": category_uid}, {"$inc": {"total_spent": -amt}}
            )

    async def _rollback_category_totals(self, tx: dict):
        """Reverse category totals."""
        ttype = tx["type"]
        amt = tx["amount"]
        category_uid = tx.get("category_uid")
        if not category_uid:
            return

        if ttype == "expense":
            inc = -amt
        elif ttype == "income":
            inc = -amt
        elif ttype == "reimburse":
            inc = amt
        else:
            return

        field = "total_spent" if ttype in ["expense", "reimburse"] else "total_earned"
        await self.db["categories"].update_one({"uid": category_uid}, {"$inc": {field: inc}})

    # ====================================================
    # ============= CATEGORY BUDGET LOGIC ================
    # ====================================================

    async def _update_budget_on_create(self, tx: dict):
        """Adjust the used portion of a category's budget."""
        ttype = tx["type"]
        amt = tx["amount"]
        category_uid = tx.get("category_uid")
        if not category_uid:
            return

        category = await self.db["categories"].find_one({"uid": category_uid})
        if not category or "budget" not in category:
            return  # no budget tracking for this category

        if ttype == "expense":
            await self.db["categories"].update_one(
                {"uid": category_uid}, {"$inc": {"budget_used": amt}}
            )
        elif ttype == "reimburse":
            await self.db["categories"].update_one(
                {"uid": category_uid}, {"$inc": {"budget_used": -amt}}
            )

    async def _rollback_budget(self, tx: dict):
        """Reverse budget changes when deleting/updating transactions."""
        ttype = tx["type"]
        amt = tx["amount"]
        category_uid = tx.get("category_uid")
        if not category_uid:
            return

        category = await self.db["categories"].find_one({"uid": category_uid})
        if not category or "budget" not in category:
            return

        if ttype == "expense":
            inc = -amt
        elif ttype == "reimburse":
            inc = amt
        else:
            return

        await self.db["categories"].update_one(
            {"uid": category_uid}, {"$inc": {"budget_used": inc}}
        )
