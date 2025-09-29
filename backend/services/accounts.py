from models.models import Account
from sqlalchemy.orm import Session
from db_schema.schema import AccountCreate 

#CRUD FOR ACCOUNTS

def new_account(db: Session, account: AccountCreate) -> Account:
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, skip: int = 0, limit: int = 100) -> list[Account]:
    return db.query(Account).offset(skip).limit(limit).all()

def get_account(db: Session, account_uid: str) -> Account | None:
    return db.query(Account).filter(Account.account_uid == account_uid).first()

def delete_account(db: Session, account_uid: str) -> bool:
    db_account = db.query(Account).filter(Account.account_uid == account_uid).first()
    if db_account:
        db.delete(db_account)
        db.commit()
        return True
    return False

def update_account_balance(db: Session, account_uid: str, new_balance: float) -> Account | None:
    db_account = db.query(Account).filter(Account.account_uid == account_uid).first()
    if db_account:
        db_account.balance = new_balance
        db.commit()
        db.refresh(db_account)
        return db_account
    return None