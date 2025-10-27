from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime, date
from uuid import uuid4

class CreditBase(BaseModel):
    """Base schema for credit/paylater tracking"""
    uid: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., description="Name of credit obligation (e.g., Credit Card, GCash PayLater)")
    provider: str = Field(..., description="Provider name (e.g., BPI, Maya, GCash)")
    credit_type: Literal["credit_card", "paylater", "installment", "loan"] = Field(..., description="Type of credit")
    
    # Amounts
    credit_limit: float = Field(ge=0, description="Total credit limit")
    current_balance: float = Field(default=0, ge=0, description="Current outstanding balance")
    available_credit: float = Field(default=0, ge=0, description="Available credit remaining")
    
    # Payment details
    due_date: Optional[date] = Field(None, description="Monthly due date (day of month)")
    minimum_payment: float = Field(default=0, ge=0, description="Minimum payment required")
    interest_rate: float = Field(default=0, ge=0, description="Annual interest rate (%)")
    
    # Metadata
    account_number: Optional[str] = Field(None, description="Last 4 digits or masked account number")
    statement_date: Optional[date] = Field(None, description="Monthly statement date")
    grace_period_days: int = Field(default=0, ge=0, description="Days before interest applies")
    
    is_active: bool = Field(default=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('available_credit', mode='before')
    @classmethod
    def calculate_available_credit(cls, v, info):
        """Auto-calculate available credit if not provided"""
        if v == 0 and 'credit_limit' in info.data and 'current_balance' in info.data:
            return info.data['credit_limit'] - info.data['current_balance']
        return v


class CreditCreate(CreditBase):
    """Schema for creating a new credit obligation"""
    pass


class CreditUpdate(BaseModel):
    """Schema for updating credit obligation"""
    name: Optional[str] = None
    provider: Optional[str] = None
    credit_limit: Optional[float] = Field(None, ge=0)
    current_balance: Optional[float] = Field(None, ge=0)
    due_date: Optional[date] = None
    minimum_payment: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(from_attributes=True)


class CreditResponse(CreditBase):
    """Schema for credit response"""
    # Additional computed fields
    utilization_rate: float = Field(default=0, description="Percentage of credit used")
    days_until_due: Optional[int] = Field(None, description="Days until next payment due")
    is_overdue: bool = Field(default=False)
    
    model_config = ConfigDict(from_attributes=True)


class CreditPayment(BaseModel):
    """Schema for recording a credit payment"""
    credit_uid: str = Field(..., description="UID of the credit obligation")
    amount: float = Field(gt=0, description="Payment amount")
    payment_date: datetime = Field(default_factory=datetime.now)
    payment_source_account_uid: Optional[str] = Field(None, description="Account used for payment")
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class CreditCharge(BaseModel):
    """Schema for recording a new charge/purchase on credit"""
    credit_uid: str = Field(..., description="UID of the credit obligation")
    amount: float = Field(gt=0, description="Charge amount")
    charge_date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = Field(None, description="What was purchased")
    category_uid: Optional[str] = Field(None, description="Expense category")
    installment_months: Optional[int] = Field(None, ge=1, description="If installment, number of months")
    notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)