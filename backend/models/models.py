from database.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

from uuid import uuid4

class Account(Base):
    __tablename__ = "accounts"

    # Table columns: id, name, balance, account_type
    account_id = Column(Integer, primary_key=True, index=True)
    account_uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    account_name = Column(String, index=True, nullable=False)
    account_type = Column(String, nullable=False) 
    balance = Column(Float, default=0.0)

class Category(Base):
    __tablename__ = "categories"

    # Table columns: id, category, amount, start_date, end_date
    category_id = Column(Integer, primary_key=True, index=True)
    category_uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    category = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    budget_used = Column(Float, default=0.0)
    frequency = Column(String, nullable=False)  # e.g., 'monthly', 'weekly'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"

    # Table columns: id, amount, category, date, description, account_id
    transaction_id = Column(Integer, primary_key=True, index=True)
    transaction_uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    date = Column(DateTime, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    category = Column(String, ForeignKey("categories.category_uid"), nullable=False)
    description = Column(String, nullable=True)
    account_id = Column(String, ForeignKey("accounts.account_uid"), nullable=False)

