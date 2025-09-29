from fastapi import FastAPI
from database.db import engine, Base, get_db, create_tables
from models import models


## initialize API
app = FastAPI()

# Create database tables
create_tables()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API"}

