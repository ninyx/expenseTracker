from models.models import Category
from sqlalchemy.orm import Session
from db_schema.schema import CategoryCreate

#CRUD FOR CATEGORIES

def new_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Category]:
    return db.query(Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_uid: str) -> Category | None:
    return db.query(Category).filter(Category.category_uid == category_uid).first()

def delete_category(db: Session, category_uid: str) -> bool:
    db_category = db.query(Category).filter(Category.category_uid == category_uid).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

def update_category(db: Session, category_uid: str, new_amount: float) -> Category | None:
    db_category = db.query(Category).filter(Category.category_uid == category_uid).first()
    if db_category:
        db_category.budget = new_amount
        db.commit()
        db.refresh(db_category)
        return db_category
    return None
