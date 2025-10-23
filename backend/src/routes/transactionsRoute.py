from ..models.categories import CategoryModel
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)
from ..models.transaction import TransactionModel
from ..database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/transactions", tags=["Transactions"])


async def enrich_transaction_with_names(tx: dict, db: AsyncIOMotorDatabase) -> dict:
    """Attach readable names for accounts/categories and enrich reimbursed transactions."""
    if not tx:
        return tx

    # Account and category lookups
    if tx.get("account_uid"):
        account = await db["accounts"].find_one({"uid": tx["account_uid"]}, {"name": 1, "_id": 0})
        tx["account_name"] = account["name"] if account else None

    if tx.get("category_uid"):
        category = await db["categories"].find_one({"uid": tx["category_uid"]}, {"name": 1, "_id": 0})
        tx["category_name"] = category["name"] if category else None

    # Transfer-related names
    if tx.get("from_account_uid"):
        from_acc = await db["accounts"].find_one({"uid": tx["from_account_uid"]}, {"name": 1, "_id": 0})
        tx["from_account_name"] = from_acc["name"] if from_acc else None

    if tx.get("to_account_uid"):
        to_acc = await db["accounts"].find_one({"uid": tx["to_account_uid"]}, {"name": 1, "_id": 0})
        tx["to_account_name"] = to_acc["name"] if to_acc else None

    # Reimbursed transaction details (nested enrichment)
    if tx.get("expense_uid"):
        reimbursed_tx = await db["transactions"].find_one({"uid": tx["expense_uid"]}, {"_id": 0})
        if reimbursed_tx:
            # Recursively enrich the reimbursed transaction as well
            reimbursed_tx = await enrich_transaction_with_names(reimbursed_tx, db)
            tx["reimbursed_transaction"] = reimbursed_tx
        else:
            tx["reimbursed_transaction"] = None

    return tx

@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    transaction_model = TransactionModel(db)
    category_model = CategoryModel(db)

    data = transaction.model_dump()
    transaction_type = data.get("transaction_type")

    # 1️⃣ Create the transaction first
    created_txn = await transaction_model.create(data)
    if not created_txn:
        raise HTTPException(status_code=400, detail="Failed to create transaction")

    # 2️⃣ Apply effects to category budgets
    if transaction_type == "expense":
        if data.get("category_uid"):
            category = await category_model.get_by_uid(data["category_uid"])
            if category:
                new_spent = category.get("total_spent", 0) + data.get("amount", 0)
                new_budget_used = category.get("budget_used", 0) + data.get("amount", 0)
                await category_model.update(category["uid"], {
                    "total_spent": new_spent,
                    "budget_used": new_budget_used
                })

    elif transaction_type == "income":
        if data.get("category_uid"):
            category = await category_model.get_by_uid(data["category_uid"])
            if category:
                new_earned = category.get("total_earned", 0) + data.get("amount", 0)
                await category_model.update(category["uid"], {
                    "total_earned": new_earned
                })

    elif transaction_type == "reimburse":
        # ✅ Reimburse should *restore* budget of linked expense’s category
        expense_uid = data.get("expense_uid")
        if not expense_uid:
            raise HTTPException(status_code=400, detail="Reimburse transaction must reference an expense_uid")

        # find the original expense transaction
        expense_txn = await transaction_model.get_by_uid(expense_uid)
        if not expense_txn:
            raise HTTPException(status_code=404, detail="Referenced expense not found")

        category_uid = expense_txn.get("category_uid")
        if category_uid:
            category = await category_model.get_by_uid(category_uid)
            if category:
                reimbursed_amount = data.get("amount", 0)
                new_budget_used = max(0, category.get("budget_used", 0) - reimbursed_amount)
                new_spent = max(0, category.get("total_spent", 0) - reimbursed_amount)
                await category_model.update(category_uid, {
                    "budget_used": new_budget_used,
                    "total_spent": new_spent
                })

    return TransactionResponse(**created_txn)


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[TransactionResponse]:
    """Get all transactions"""
    transaction_model = TransactionModel(db)
    transactions = await transaction_model.get_all()

    # Preload all account/category names for efficiency
    accounts = {
        acc["uid"]: acc["name"]
        async for acc in db["accounts"].find({}, {"uid": 1, "name": 1, "_id": 0})
    }
    categories = {
        cat["uid"]: cat["name"]
        async for cat in db["categories"].find({}, {"uid": 1, "name": 1, "_id": 0})
    }

    enriched_transactions = []
    for tx in transactions:
        # Add readable names
        tx["account_name"] = accounts.get(tx.get("account_uid"))
        tx["category_name"] = categories.get(tx.get("category_uid"))
        tx["from_account_name"] = accounts.get(tx.get("from_account_uid"))
        tx["to_account_name"] = accounts.get(tx.get("to_account_uid"))

        # Include full reimbursed transaction details
        if tx.get("expense_uid"):
            reimbursed_tx = await db["transactions"].find_one({"uid": tx["expense_uid"]}, {"_id": 0})
            if reimbursed_tx:
                reimbursed_tx = await enrich_transaction_with_names(reimbursed_tx, db)
                tx["reimbursed_transaction"] = reimbursed_tx

        enriched_transactions.append(TransactionResponse(**tx))

    return enriched_transactions


@router.get("/{uid}", response_model=TransactionResponse)
async def get_transaction(uid: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> TransactionResponse:
    """Get a specific transaction by UID"""
    transaction_model = TransactionModel(db)
    transaction = await transaction_model.get_by_uid(uid)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with UID {uid} not found"
        )

    transaction = await enrich_transaction_with_names(transaction, db)
    return TransactionResponse(**transaction)


@router.patch("/{uid}", response_model=TransactionResponse)
async def update_transaction(
    uid: str,
    tx_data: TransactionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> TransactionResponse:
    """Update an existing transaction"""
    transaction_model = TransactionModel(db)
    existing = await transaction_model.get_by_uid(uid)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with UID {uid} not found"
        )
    
    updated = await transaction_model.update(uid, tx_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update transaction"
        )

    updated = await enrich_transaction_with_names(updated, db)
    return TransactionResponse(**updated)


@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_transaction(uid: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> dict:
    """Delete a transaction"""
    transaction_model = TransactionModel(db)
    existing = await transaction_model.get_by_uid(uid)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with UID {uid} not found"
        )
    
    success = await transaction_model.delete(uid)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete transaction"
        )

    return {"status": "deleted", "uid": uid}
