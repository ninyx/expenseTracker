from models.models import Transaction, Account, Category
from sqlalchemy.orm import Session
from db_schema.schema import TransactionCreate, AccountCreate, CategoryCreate

#CRUD FOR CATEGORIES
def new_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> list[Transaction]:
    return db.query(Transaction).offset(skip).limit(limit).all()