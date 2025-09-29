from fastapi import APIRouter, Depends, HTTPException
from database.db import engine, Base, get_db, create_tables
from models import models
from sqlalchemy.orm import Session
from services import categories
from db_schema import schema
from datetime import datetime, timedelta

# category ROUTES

category_route = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Not found"}},
)


@category_route.post("/", response_model=schema.Category)
def new_category(category: schema.CategoryCreate, db: Session = Depends(get_db)):
    match category.frequency:
        case "monthly":
            category.end_date = category.start_date + timedelta(days=30)
        case "weekly":
            category.end_date = category.start_date + timedelta(days=7)
        case "biweekly":
            category.end_date = category.start_date + timedelta(days=14)
        case "yearly":
            category.end_date = category.start_date + timedelta(days=365)
        case _:
            raise HTTPException(status_code=400, detail="Invalid frequency value")
    
    return categories.new_category(db, category)

@category_route.get("/", response_model=list[schema.Category])
def get_categories(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return categories.get_categories(db, skip=skip, limit=limit)

@category_route.get("/{category_uid}", response_model=schema.Category)
def get_category(category_uid: str, db: Session = Depends(get_db)):
    db_category = categories.get_category(db, category_uid=category_uid)
    if db_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    return db_category

@category_route.delete("/{category_uid}", response_model=dict)
def delete_category(category_uid: str, db: Session = Depends(get_db)):
    success = categories.delete_category(db, category_uid=category_uid)
    if not success:
        raise HTTPException(status_code=404, detail="category not found")
    return {"detail": "category deleted successfully"}

@category_route.put("/{category_uid}/balance", response_model=schema.Category)
def update_category_balance(category_uid: str, new_balance: float, db: Session = Depends(get_db)):
    db_category = categories.update_category(db, category_uid=category_uid, new_amount=new_balance)
    if db_category is None:
        raise HTTPException(status_code=404, detail="category not found")
    return db_category