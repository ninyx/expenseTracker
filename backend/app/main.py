from fastapi import FastAPI, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import accounts, transactions
from db_schema import schema
from datetime import datetime
from routes import account_routes

## initialize API
app = FastAPI()

# Create database tables
create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API"}

# ACCOUNT ROUTES 

app.include_router(account_routes.account_route)
