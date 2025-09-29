from pydantic import BaseModel
from datetime import datetime   
from uuid import uuid4


class AccountBase(BaseModel):
    account_name: str
    account_type: str
    balance: float

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    account_id: int
    account_uid: str
    class config:
        from_attribute = True

class CategoryBase(BaseModel):
    category: str
    budget: float
    frequency: str  # e.g., 'monthly', 'weekly'


class CategoryCreate(CategoryBase):
    start_date: datetime
    end_date: datetime | None = None
    pass

class Category(CategoryBase):
    category_id: int
    category_uid: str
    budget_used: float
    start_date: datetime
    end_date: datetime | None
    class config:
        from_attribute = True

# class TransactionBase(BaseModel):
#     transaction_type: str  
#     amount: float
#     description: str | None

# class TransactionCreate(TransactionBase):
#     category_uid: str
#     account_uid: str
#     date: datetime

# class Transaction(TransactionBase):
#     transaction_uid: str
#     category_uid: str
#     account_uid: str
#     date: datetime
#     class config:
#         from_attribute = True

class TransactionBase(BaseModel):
    transaction_type: str  # 'income', 'expense', 'reimbursement', 'transfer'
    amount: float
    description: str | None = None
    date: datetime

class TransactionCreate(TransactionBase):
    # For income/expense/reimbursement
    category_uid: str | None = None
    account_uid: str | None = None

    # For transfers
    source_account_uid: str | None = None
    destination_account_uid: str | None = None
    transfer_fee: float = 0.0

class Transaction(TransactionBase):
    transaction_uid: str
    category_uid: str | None
    account_uid: str | None
    source_account_uid: str | None
    destination_account_uid: str | None
    transfer_fee: float

    class config:
        from_attribute = True