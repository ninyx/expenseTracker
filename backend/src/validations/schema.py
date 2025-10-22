from jsonschema import validate, ValidationError
from fastapi import HTTPException, status
from datetime import datetime

transaction_schema = {
    "type": "object",
    "properties": {
        "uid": {"type": "string"},
        "type": {"enum": ["income", "expense", "reimburse", "transfer"]},
        "date": {"type": ["string", "null"], "format": "date-time"},
        "amount": {"type": "number", "minimum": 0},
        "account_uid": {"type": ["string", "null"]},
        "category_uid": {"type": ["string", "null"]},
        "description": {"type": ["string", "null"]},
        "transfer_fee": {"type": ["number", "null"], "minimum": 0},
        "from_account_uid": {"type": ["string", "null"]},
        "to_account_uid": {"type": ["string", "null"]},
        "expense_uid": {"type": ["string", "null"]}
    },
    # uid will be generated automatically by model, not required in input
    "required": ["type", "amount"],
    "additionalProperties": False
}


def validate_transaction(tx: dict):
    try:
        validate(instance=tx, schema=transaction_schema)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transaction data: {e.message}"
        )

account_schema = {
    "type": "object",
    "properties": {
        "uid": {"type": "string"},
        "name": {"type": "string"},
        "type": {"enum": ["checking", "savings", "credit", "loan"]},
        "balance": {"type": "number", "minimum": 0},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
    },
    "required": ["name", "type", "balance"],
    "additionalProperties": False
}


def validate_account(account: dict):
    try:
        validate(instance=account, schema=account_schema)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid account data: {e.message}"
        )
    
category_schema = {
    "type": "object",
    "properties": {
        "uid": {"type": "string"},
        "name": {"type": "string"},
        "is_active": {"type": "boolean"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
    },
    "required": ["name"],
    "additionalProperties": False
}


def validate_category(category: dict):
    try:
        validate(instance=category, schema=category_schema)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category data: {e.message}"
        )
