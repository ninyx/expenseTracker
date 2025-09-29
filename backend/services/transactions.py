from models.models import Transaction
from sqlalchemy.orm import Session
from db_schema.schema import TransactionCreate
from fastapi import HTTPException

#CRUD FOR CATEGORIES

def new_transaction(db: Session, transaction: TransactionCreate):
    # Validate required fields based on transaction_type
    if transaction.transaction_type == "transfer":
        if not transaction.source_account_uid or not transaction.destination_account_uid:
            raise HTTPException(status_code=400, detail="Transfer must have source and destination accounts")
    else:
        if not transaction.account_uid or not transaction.category_uid:
            raise HTTPException(status_code=400, detail="Non-transfer transactions must have account and category")
    
    db_transaction = Transaction(
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        date=transaction.date,
        category_uid=transaction.category_uid,
        account_uid=transaction.account_uid,
        source_account_uid=transaction.source_account_uid,
        destination_account_uid=transaction.destination_account_uid,
        transfer_fee=transaction.transfer_fee
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 10):  
    return db.query(Transaction).offset(skip).limit(limit).all()

def get_transaction(db: Session, transaction_uid: str) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.transaction_uid == transaction_uid).first()

def delete_transaction(db: Session, transaction_uid: str) -> bool:
    db_transaction = db.query(Transaction).filter(Transaction.transaction_uid == transaction_uid).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False

def update_transaction(db: Session, transaction_uid: str, new_amount: float) -> Transaction | None:
    db_transaction = db.query(Transaction).filter(Transaction.transaction_uid == transaction_uid).first()
    if db_transaction:
        db_transaction.amount = new_amount
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    return None

# Additional functions can be added as needed