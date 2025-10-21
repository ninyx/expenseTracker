# backend/src/routes/accounts.py
from fastapi import APIRouter, HTTPException
from ..models import AccountModel
from .. import database

router = APIRouter(tags=["accounts"])

@router.post("/", status_code=201)
async def create_account(payload: AccountModel):
    db = database.db
    doc = payload.dict()
    try:
        result = await db.accounts.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"_id": str(result.inserted_id)}

@router.get("/")
async def list_accounts():
    db = database.db
    cursor = db.accounts.find()
    return [ {**doc, "_id": str(doc["_id"])} async for doc in cursor ]
