from database.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

class Account(Base):
    __tablename__ = "accounts"

    # Table columns: id, name, balance, account_type
    account_id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, nullable=False) 
    balance = Column(Float, default=0.0)

class Category(Base):
    __tablename__ = "categories"

    # Table columns: id, category, amount, start_date, end_date
    category_id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"

    # Table columns: id, amount, category, date, description, account_id
    transaction_id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'income' or 'expense'
    amount = Column(Float, nullable=False)
    category = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    description = Column(String, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)

