# app/crud/transaction_crud.py
from typing import List, Optional
from bson import ObjectId
from .. import database as db
from ..model import Transaction
from fastapi import HTTPException, status
from datetime import datetime
from uuid import uuid4

collection = lambda: db.db.transactions

async def create_transaction(data: dict) -> Transaction:
    result = await collection().insert_one(data)
    new_tx = await collection().find_one({"_id": result.inserted_id})
    return Transaction(**new_tx)


async def get_all_transactions() -> List[Transaction]:
    transactions = await collection().find().to_list(1000)
    return [Transaction(**tx) for tx in transactions]


async def get_transaction(uid: str) -> Optional[Transaction]:
    tx = await collection().find_one({"uid": uid})
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return Transaction(**tx)


async def update_transaction(uid: str, data: dict) -> Transaction:
    result = await collection().update_one({"uid": uid}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or not modified")
    updated = await collection().find_one({"uid": uid})
    return Transaction(**updated)


async def delete_transaction(uid: str):
    result = await collection().delete_one({"uid": uid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return {"status": "deleted", "uid": uid}
