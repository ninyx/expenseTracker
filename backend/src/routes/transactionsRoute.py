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
    return TransactionResponse(**result)

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[TransactionResponse]:
    """Get all transactions"""
    transaction_model = TransactionModel(db)
    transactions = await transaction_model.get_all()
    return [TransactionResponse(**tx) for tx in transactions]

@router.get("/{uid}", response_model=TransactionResponse)
async def get_transaction(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> TransactionResponse:
    """Get a specific transaction by UID"""
    transaction_model = TransactionModel(db)
    transaction = await transaction_model.get_by_uid(uid)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with UID {uid} not found"
        )
    return TransactionResponse(**transaction)

@router.patch("/{uid}", response_model=TransactionResponse)
async def update_transaction(
    uid: str,
    tx_data: TransactionUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> TransactionResponse:
    """Update an existing transaction"""
    transaction_model = TransactionModel(db)
    # First check if transaction exists
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
    return TransactionResponse(**updated)

@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_transaction(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Delete a transaction"""
    transaction_model = TransactionModel(db)
    # First check if transaction exists
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
