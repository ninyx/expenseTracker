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


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    tx: TransactionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> TransactionResponse:
    """Create a new transaction"""
    transaction_model = TransactionModel(db)
    result = await transaction_model.create(tx.model_dump())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create transaction"
        )

    # Add display data before returning
    result = await enrich_transaction_with_names(result, db)
    return TransactionResponse(**result)


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
