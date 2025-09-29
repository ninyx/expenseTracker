from pydantic import BaseModel
from datetime import datetime   
from uuid import uuid4


class AccountBase(BaseModel):
    account_name: str
    account_type: str
    balance: float

class AccountCreate(AccountBase):
    account_uid: str = str(uuid4())
    pass

class Account(AccountBase):
    account_id: int
    account_uid: str
    class config:
        from_attribute = True

class CategoryBase(BaseModel):
    category: str
    amount: float

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: int
    class config:
        from_attribute = True

class TransactionBase(BaseModel):
    transaction_type: str  # 'income' or 'expense'
    amount: float
    description: str | None

class TransactionCreate(TransactionBase):
    category: int
    account_id: int
    date: datetime = datetime.now()

class Transaction(TransactionBase):
    transaction_id: int
    category: int
    account_id: int
    date: datetime

    class config:
        from_attribute = True