"""Base schemas and common validators."""
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

class MongoModel(BaseModel):
    """Base model with MongoDB support."""
    uid: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }