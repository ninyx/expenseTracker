from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class AccountBase(BaseModel):
    """Base schema for account data shared between create and response"""
    uid: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the account")
    name: str = Field(..., description="Name of the account")
    type: Literal["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]
    balance: float = Field(default=0, ge=0, description="Balance must be greater than or equal to 0")
    created_at: datetime = Field(default_factory=datetime.now)
    interest_rate: Optional[float] = Field(default=0, ge=0, description="Annual interest rate as percentage")
    interest_frequency: Optional[Literal["monthly", "quarterly", "annually"]] = Field(default="monthly")

class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    description: Optional[str] = None

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is non-negative."""
        if v < 0:
            raise ValueError('Balance must be greater than or equal to 0')
        return v

    @field_validator('interest_rate')
    @classmethod
    def validate_interest_rate(cls, v):
        """Ensure interest rate is non-negative and reasonable."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Interest rate must be between 0 and 100')
        return v

    model_config = ConfigDict(from_attributes=True)


class AccountUpdate(BaseModel):
    """Schema for updating an existing account"""
    name: Optional[str] = None
    type: Optional[Literal["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]] = None
    balance: Optional[float] = Field(None, ge=0, description="Balance must be greater than or equal to 0")
    description: Optional[str] = None
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    interest_frequency: Optional[Literal["monthly", "quarterly", "annually"]] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError('Balance must be greater than or equal to 0')
        return v

    @field_validator('interest_rate')
    @classmethod
    def validate_interest_rate(cls, v):
        """Ensure interest rate is valid if provided."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Interest rate must be between 0 and 100')
        return v

    model_config = ConfigDict(from_attributes=True)

class AccountResponse(AccountBase):
    """Schema for account data returned in responses"""
    uid: str
    name: str
    type: Literal["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]
    balance: float
    description: Optional[str] = None
    interest_rate: Optional[float] = 0
    interest_frequency: Optional[Literal["monthly", "quarterly", "annually"]] = "monthly"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)