from fastapi import APIRouter, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import transactions
from db_schema import schema
from datetime import datetime, timedelta

# transaction ROUTES

transaction_route = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)


@transaction_route.post("/", response_model=schema.Transaction)
def create_transaction(transaction: schema.TransactionCreate, db: Session = Depends(get_db)):
    return transactions.new_transaction(db, transaction)

@transaction_route.get("/", response_model=list[schema.Transaction])
def get_transactions(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return transactions.get_transactions(db, skip=skip, limit=limit)

@transaction_route.get("/{transaction_uid}", response_model=schema.Transaction)
def get_transaction(transaction_uid: str, db: Session = Depends(get_db)):
    db_transaction = transactions.get_transaction(db, transaction_uid=transaction_uid)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@transaction_route.delete("/{transaction_uid}", response_model=dict)
def delete_transaction(transaction_uid: str, db: Session = Depends(get_db)):
    success = transactions.delete_transaction(db, transaction_uid=transaction_uid)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted successfully"}

@transaction_route.put("/{transaction_uid}/amount", response_model=schema.Transaction)
def update_transaction_amount(transaction_uid: str, new_amount: float, db: Session = Depends(get_db)):
    db_transaction = transactions.update_transaction(db, transaction_uid=transaction_uid, new_amount=new_amount)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction
