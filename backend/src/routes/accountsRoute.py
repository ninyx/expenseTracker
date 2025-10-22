from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..schemas.accounts import (
    AccountCreate,
    AccountUpdate,
    AccountResponse
)
from ..models.accounts import AccountModel
from ..database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AccountResponse:
    """Create a new account"""
    account_model = AccountModel(db)
    result = await account_model.create(account.model_dump())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create account"
        )
    return AccountResponse(**result)

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[AccountResponse]:
    """Get all accounts"""
    account_model = AccountModel(db)
    accounts = await account_model.get_all()
    return [AccountResponse(**acc) for acc in accounts]

@router.get("/{uid}", response_model=AccountResponse)
async def get_account(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AccountResponse:
    """Get a specific account by UID"""
    account_model = AccountModel(db)
    account = await account_model.get_by_uid(uid)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with UID {uid} not found"
        )
    return AccountResponse(**account)

@router.patch("/{uid}", response_model=AccountResponse)
async def update_account(
    uid: str,
    acc_data: AccountUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> AccountResponse:
    """Update an existing account"""
    account_model = AccountModel(db)
    updated_account = await account_model.update(uid, acc_data.model_dump(exclude_unset=True))
    if not updated_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with UID {uid} not found or not modified"
        )
    return AccountResponse(**updated_account)

@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_account(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Delete an account"""
    account_model = AccountModel(db)
    deleted = await account_model.delete(uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with UID {uid} not found"
        )
    return {"status": "deleted", "uid": uid}