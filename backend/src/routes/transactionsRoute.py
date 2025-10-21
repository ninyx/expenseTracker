# app/routes/transaction_routes.py
from fastapi import APIRouter, HTTPException
from typing import List
from ..model import Transaction
from ..crud.transactions import (
    create_transaction, get_all_transactions, get_transaction,
    update_transaction, delete_transaction
)
from ..validations.schema import validate_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])

from datetime import datetime
from bson import ObjectId

def serialize_data(data):
    """Recursively converts datetime and ObjectId objects for JSON storage."""
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@router.post("/", response_model=Transaction)
async def create_tx(tx: Transaction):
     # ✅ Step 1: If no date, set it
    if "date" not in tx.dict() or not tx.dict()["date"]:
        tx.date = datetime.now()

    # ✅ Step 2: Convert datetime → string before validating
    clean_data = serialize_data(tx.dict())

    validate_transaction(clean_data)
    return await create_transaction(clean_data)


@router.get("/", response_model=List[Transaction])
async def list_transactions():
    return await get_all_transactions()


@router.get("/{uid}", response_model=Transaction)
async def get_tx(uid: str):
    return await get_transaction(uid)


@router.patch("/{uid}", response_model=Transaction)
async def patch_transaction(uid: str, tx_data: dict):
    # 1️⃣ Prevent editing UID
    if "uid" in tx_data:
        tx_data.pop("uid")

    # 2️⃣ Serialize (e.g. handle datetime objects)
    clean_data = serialize_data(tx_data)

    # 3️⃣ Perform update (merge with existing)
    return await update_transaction(uid, clean_data)


@router.delete("/{uid}")
async def delete_tx(uid: str):
    return await delete_transaction(uid)
