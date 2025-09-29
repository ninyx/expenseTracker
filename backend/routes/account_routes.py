from fastapi import APIRouter, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import accounts
from db_schema import schema

# ACCOUNT ROUTES

account_route = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)


@account_route.post("/", response_model=schema.Account)
def new_account(account: schema.AccountCreate, db: Session = Depends(get_db)):
    return accounts.new_account(db, account)

@account_route.get("/", response_model=list[schema.Account])
def get_accounts(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return accounts.get_accounts(db, skip=skip, limit=limit)

@account_route.get("/{account_uid}", response_model=schema.Account)
def get_account(account_uid: str, db: Session = Depends(get_db)):
    db_account = accounts.get_account(db, account_uid=account_uid)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@account_route.delete("/{account_uid}", response_model=dict)
def delete_account(account_uid: str, db: Session = Depends(get_db)):
    success = accounts.delete_account(db, account_uid=account_uid)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"detail": "Account deleted successfully"}

@account_route.put("/{account_uid}/balance", response_model=schema.Account)
def update_account_balance(account_uid: str, new_balance: float, db: Session = Depends(get_db)):
    db_account = accounts.update_account_balance(db, account_uid=account_uid, new_balance=new_balance)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account