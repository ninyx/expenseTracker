# app/crud/transaction_crud.py
from typing import List, Optional
from bson import ObjectId
from .. import database as db
from ..model import Transaction
from fastapi import HTTPException, status
from datetime import datetime
from uuid import uuid4

from src.database import get_db

async def get_collection():
    db = await get_db()
    return db["transactions"]


async def create_transaction(data: dict) -> Transaction:
    db = await get_db()
    result = await db["transactions"].insert_one(data)
    new_tx = await db["transactions"].find_one({"_id": result.inserted_id})
    return Transaction(**new_tx)


async def get_all_transactions() -> List[Transaction]:
    db = await get_db()
    transactions = await db["transactions"].find().to_list(1000)
    return [Transaction(**tx) for tx in transactions]


async def get_transaction(uid: str) -> Optional[Transaction]:
    db = await get_db()
    tx = await db["transactions"].find_one({"uid": uid})
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return Transaction(**tx)


async def update_transaction(uid: str, data: dict) -> Transaction:
    db = await get_db()
    result = await db["transactions"].update_one({"uid": uid}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or not modified")
    updated = await db["transactions"].find_one({"uid": uid})
    return Transaction(**updated)


async def delete_transaction(uid: str):
    db = await get_db()
    result = await db["transactions"].delete_one({"uid": uid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return {"status": "deleted", "uid": uid}
