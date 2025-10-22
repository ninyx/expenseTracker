from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class TransactionBase(BaseModel):
    """Base schema for transaction data shared between create and response"""
    uid: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["income", "expense", "reimburse", "transfer"]
    amount: float = Field(gt=0, description="Amount must be greater than 0")
    description: Optional[str] = None
    

class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    account_uid: Optional[str] = None
    category_uid: Optional[str] = None
    transfer_fee: Optional[float] = None
    from_account_uid: Optional[str] = None
    to_account_uid: Optional[str] = None
    expense_uid: Optional[str] = None
    date: datetime = Field(default_factory=datetime.now)

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive."""
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

    @field_validator('transfer_fee')
    @classmethod
    def validate_transfer_fee(cls, v):
        """Ensure transfer fee is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError('Transfer fee cannot be negative')
        return v

    @model_validator(mode="after")
    def validate_type_specific_fields(self):
        """Validate required fields based on transaction type."""
        if self.type == "reimburse":
            if not self.expense_uid:
                raise ValueError("Reimburse transactions require expense_uid")
            if not self.account_uid:
                raise ValueError("Reimburse transactions require account_uid")
        
        elif self.type == "transfer":
            if not self.from_account_uid or not self.to_account_uid:
                raise ValueError("Transfer transactions require from_account_uid and to_account_uid")
        
        elif self.type in ["income", "expense"]:
            if not self.account_uid:
                raise ValueError(f"{self.type.capitalize()} transactions require account_uid")
            if not self.category_uid:
                raise ValueError(f"{self.type.capitalize()} transactions require category_uid")
        
        return self


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction"""
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    category_uid: Optional[str] = None
    transfer_fee: Optional[float] = Field(None, ge=0)

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Ensure amount is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

    @field_validator('transfer_fee')
    @classmethod
    def validate_transfer_fee(cls, v):
        """Ensure transfer fee is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError('Transfer fee cannot be negative')
        return v
class TransactionResponse(TransactionBase):
    """Schema for transaction response from API"""
    uid: str
    type: Literal["income", "expense", "reimburse", "transfer"]
    date: datetime
    amount: float
    description: Optional[str] = None
    account_uid: Optional[str] = None
    category_uid: Optional[str] = None
    transfer_fee: Optional[float] = None
    from_account_uid: Optional[str] = None
    to_account_uid: Optional[str] = None
    expense_uid: Optional[str] = None

    # Display-only fields
    account_name: Optional[str] = None
    category_name: Optional[str] = None
    from_account_name: Optional[str] = None
    to_account_name: Optional[str] = None

    # 👇 Add full details of reimbursed expense
    reimbursed_transaction: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
