from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Literal, List
from datetime import datetime
from uuid import uuid4

# -------------------------
# Base Schema
# -------------------------
class CategoryBase(BaseModel):
    """Base schema for category data shared between create and response"""
    uid: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category")
    description: Optional[str] = None
    transaction_type: Literal["income", "expense"] = Field(..., description="Type of transaction for the category")
    budgeted_amount: Optional[float] = Field(None, ge=0, description="Budgeted amount must be non-negative if provided")
    frequency: Optional[Literal["monthly", "weekly", "yearly", "one-time"]] = None
    parent_uid: Optional[str] = Field(None, description="Parent category UID if this is a sub-category")
    is_active: bool = Field(default=True, description="Flag to indicate if the category is active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(from_attributes=True)

    # -------------------------
    # Hierarchy Validation
    # -------------------------
    @model_validator(mode="before")
    def check_parent_not_self(cls, values):
        if values.get("uid") and values.get("parent_uid") and values["uid"] == values["parent_uid"]:
            raise ValueError("Category cannot be its own parent")
        return values

# -------------------------
# Create Schema
# -------------------------
class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    model_config = ConfigDict(from_attributes=True)

# -------------------------
# Update Schema
# -------------------------
class CategoryUpdate(BaseModel):
    """Schema for updating an existing category"""
    name: Optional[str] = None
    description: Optional[str] = None
    transaction_type: Optional[Literal["income", "expense"]] = None
    budgeted_amount: Optional[float] = Field(None, ge=0)
    frequency: Optional[Literal["monthly", "weekly", "yearly", "one-time"]] = None
    parent_uid: Optional[str] = None
    is_active: Optional[bool] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    def check_parent_not_self(cls, values):
        if values.get("parent_uid") and values.get("uid") and values["uid"] == values["parent_uid"]:
            raise ValueError("Category cannot be its own parent")
        return values

# -------------------------
# Response Schema
# -------------------------
class CategoryResponse(CategoryBase):
    """Schema for category response with optional nested children"""
    children: Optional[List["CategoryResponse"]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

# Needed for forward references in Pydantic
CategoryResponse.model_rebuild()
