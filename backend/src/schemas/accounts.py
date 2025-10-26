from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class AccountBase(BaseModel):
    """Base schema for account data shared between create and response"""
    uid: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the account")
    name: str = Field(..., description="Name of the account")
    type: Literal["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]
    balance: float = Field(gt=0, description="Balance must be greater than 0")
    created_at: datetime = Field(default_factory=datetime.now)

class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    description: Optional[str] = None
    interest_rate: Optional[float] = None

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is positive."""
        if v < 0:
            raise ValueError('Balance must be greater than or equal to 0')
        return v

    model_config = ConfigDict(from_attributes=True)


class AccountUpdate(BaseModel):
    """Schema for updating an existing account"""
    name: Optional[str] = None
    type: Optional[Literal["checking", "savings", "credit", "loan"]] = None
    balance: Optional[float] = Field(None, gt=0, description="Balance must be greater than 0")
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    interest_rate: Optional[float] = None

    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v):
        """Ensure balance is positive if provided."""
        if v is not None and v < 0:
            raise ValueError('Balance must be greater than or equal to 0')
        return v

    model_config = ConfigDict(from_attributes=True)

class AccountResponse(AccountBase):
    """Schema for account data returned in responses"""
    uid: str
    name: str
    type: Literal["cash", "checking", "savings", "credit card", "loan", "mortgage", "investment", "retirement", "digital wallet"]
    balance: float
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    interest_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
