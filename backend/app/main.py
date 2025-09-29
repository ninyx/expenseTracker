from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

# Feature Add: Rate Limiting

app = FastAPI(title="Expense Tracker")

## Establish routes for GET, POST, PUT, DELETE requests

## Establish connection to DB