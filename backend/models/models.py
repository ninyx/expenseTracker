from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()


# ==============================
# ACCOUNTS SCHEMA
# ==============================

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    type_uid = Column(String, ForeignKey("account_types.uid"), nullable=False)
    balance = Column(Float, nullable=False, default=0.0)

    types = relationship("AccountType", back_populates="accounts")
    transactions = relationship("TransactionExpense", back_populates="account")
    incomes = relationship("TransactionIncome", back_populates="account")
    reimbursements = relationship("TransactionReimbursement", back_populates="account")
    transfers_src = relationship("TransactionTransfer", foreign_keys="TransactionTransfer.src_account_uid", back_populates="src_account")
    transfers_dest = relationship("TransactionTransfer", foreign_keys="TransactionTransfer.dest_account_uid", back_populates="dest_account")


class AccountType(Base):
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False)  # e.g. 'Checking', 'Savings', 'Credit'

    accounts = relationship("Account", back_populates="type")


# ==============================
# CATEGORIES SCHEMA
# ==============================

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)

    budgets = relationship("CategoryBudget", back_populates="category")
    expenses = relationship("TransactionExpense", back_populates="category")
    incomes = relationship("TransactionIncome", back_populates="category")
    reimbursements = relationship("TransactionReimbursement", back_populates="category")


class CategoryBudget(Base):
    __tablename__ = "category_budgets"

    id = Column(Integer, primary_key=True, index=True)
    category_uid = Column(String, ForeignKey("categories.uid"), nullable=False)
    budget = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)  # e.g., 'monthly', 'weekly'
    start_date = Column(DateTime, nullable=False, default=datetime.now)
    end_date = Column(DateTime, nullable=True)

    category = relationship("Category", back_populates="budgets")


# ==============================
# TRANSACTIONS SCHEMA
# ==============================

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4())) 
    type_uid = Column(String, ForeignKey("transaction_types.uid"), nullable=False)

    type = relationship("TransactionType", back_populates="transactions")


class TransactionType(Base):
    __tablename__ = "transaction_types"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    name = Column(String, unique=True, nullable=False)  # e.g. 'income', 'expense', 'transfer'

    transactions = relationship("Transaction", back_populates="type")


class TransactionExpense(Base):
    __tablename__ = "transaction_expenses"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    transaction_uid = Column(String, ForeignKey("transactions.uid"), nullable=False)
    type_uid = Column(String, ForeignKey("transaction_types.uid"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(Float, nullable=False)
    account_uid = Column(String, ForeignKey("accounts.uid"), nullable=False)
    category_uid = Column(String, ForeignKey("categories.uid"), nullable=False)
    description = Column(String, nullable=True)

    transaction = relationship("Transaction")
    type = relationship("TransactionType")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="expenses")


class TransactionIncome(Base):
    __tablename__ = "transaction_incomes"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    transaction_uid = Column(String, ForeignKey("transactions.uid"), nullable=False)
    type_uid = Column(String, ForeignKey("transaction_types.uid"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(Float, nullable=False)
    account_uid = Column(String, ForeignKey("accounts.uid"), nullable=False)
    category_uid = Column(String, ForeignKey("categories.uid"), nullable=False)
    description = Column(String, nullable=True)

    transaction = relationship("Transaction")
    type = relationship("TransactionType")
    account = relationship("Account", back_populates="incomes")
    category = relationship("Category", back_populates="incomes")


class TransactionReimbursement(Base):
    __tablename__ = "transaction_reimbursements"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    transaction_uid = Column(String, ForeignKey("transactions.uid"), nullable=False)
    type_uid = Column(String, ForeignKey("transaction_types.uid"), nullable=False)
    expense_transaction_uid = Column(String, ForeignKey("transaction_expenses.uid"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(Float, nullable=False)
    account_uid = Column(String, ForeignKey("accounts.uid"), nullable=False)
    category_uid = Column(String, ForeignKey("categories.uid"), nullable=False)
    description = Column(String, nullable=True)

    transaction = relationship("Transaction")
    type = relationship("TransactionType")
    expense_transaction = relationship("TransactionExpense")
    account = relationship("Account", back_populates="reimbursements")
    category = relationship("Category", back_populates="reimbursements")


class TransactionTransfer(Base):
    __tablename__ = "transaction_transfers"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True, nullable=False, default=lambda: str(uuid4()))
    transaction_uid = Column(String, ForeignKey("transactions.uid"), nullable=False)
    type_uid = Column(String, ForeignKey("transaction_types.uid"), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(Float, nullable=False)
    transfer_fee = Column(Float, nullable=False, default=0.0)
    src_account_uid = Column(String, ForeignKey("accounts.uid"), nullable=False)
    dest_account_uid = Column(String, ForeignKey("accounts.uid"), nullable=False)
    description = Column(String, nullable=True)

    transaction = relationship("Transaction")
    type = relationship("TransactionType")
    src_account = relationship("Account", foreign_keys=[src_account_uid], back_populates="transfers_src")
    dest_account = relationship("Account", foreign_keys=[dest_account_uid], back_populates="transfers_dest")
