from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4
# ---------------- Accounts ----------------
class Account(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    type: str
    balance: float

# ---------------- Account Types ----------------
class AccountType(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    name: str

# ---------------- Categories ----------------
class Category(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    name: str

# ---------------- Category Budget ----------------
class CategoryBudget(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    category_uid: str
    budget: float
    frequency: str

# ---------------- Frequency ----------------
class Frequency(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    start_date: datetime
    end_date: datetime

# ---------------- Transactions ----------------
class Transaction(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["income", "expense", "reimburse", "transfer"]
    date: datetime = Field(default_factory=datetime.now)
    amount: float
    account_uid: Optional[str] = None
    category_uid: Optional[str] = None
    description: Optional[str] = None
    transfer_fee: Optional[float] = None

    from_account_uid: Optional[str] = None
    to_account_uid: Optional[str] = None
    expense_uid: Optional[str] = None
    

    @model_validator(mode="after")
    def validate_transfer_fields(self):
        """Ensure transfer transactions have both from/to accounts."""
        if self.type == "reimburse":
            if not self.expense_uid:
                raise ValueError("Reimburse transactions require expense_uid")
        elif self.type == "transfer":
            if not self.from_account_uid or not self.to_account_uid:
                raise ValueError("Transfer transactions require from_account_uid and to_account_uid")
        return self