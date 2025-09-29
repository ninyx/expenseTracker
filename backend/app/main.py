from fastapi import FastAPI, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import accounts, transactions
from db_schema import schema
from datetime import datetime
from routes import account_routes, categories_routes, transaction_routes

## initialize API
app = FastAPI()

# Create database tables
create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API"}

# ACCOUNT TABLE ROUTES 
app.include_router(account_routes.account_route)

# CATEGORY TABLE ROUTES
app.include_router(categories_routes.category_route)

# TRANSACTION TABLE ROUTES
app.include_router(transaction_routes.transaction_route)