from fastapi import FastAPI, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import accounts, transactions
from db_schema import schema
from datetime import datetime

## initialize API
app = FastAPI()

# Create database tables
create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API"}

# ACCOUNT ROUTES

@app.post("/accounts/", response_model=schema.Account)
def new_account(account: schema.AccountCreate, db: Session = Depends(get_db)):
    return accounts.new_account(db, account)

@app.get("/accounts/", response_model=list[schema.Account])
def get_accounts(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return accounts.get_accounts(db, skip=skip, limit=limit)

@app.get("/accounts/{account_uid}", response_model=schema.Account)
def get_account(account_uid: str, db: Session = Depends(get_db)):
    db_account = accounts.get_account(db, account_uid=account_uid)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete("/accounts/{account_uid}", response_model=dict)
def delete_account(account_uid: str, db: Session = Depends(get_db)):
    success = accounts.delete_account(db, account_uid=account_uid)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"detail": "Account deleted successfully"}

@app.put("/accounts/{account_uid}/balance", response_model=schema.Account)
def update_account_balance(account_uid: str, new_balance: float, db: Session = Depends(get_db)):
    db_account = accounts.update_account_balance(db, account_uid=account_uid, new_balance=new_balance)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account