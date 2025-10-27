from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..schemas.credit import (
    CreditCreate,
    CreditUpdate,
    CreditResponse,
    CreditPayment,
    CreditCharge,
)
from ..models.credit import CreditModel
from ..database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/credits", tags=["Credits"])


@router.post("/", response_model=CreditResponse, status_code=status.HTTP_201_CREATED)
async def create_credit(
    credit: CreditCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CreditResponse:
    """Create a new credit/paylater obligation"""
    credit_model = CreditModel(db)
    result = await credit_model.create(credit.model_dump())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create credit"
        )
    return CreditResponse(**result)


@router.get("/", response_model=List[CreditResponse])
async def get_credits(
    active_only: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[CreditResponse]:
    """Get all credit obligations"""
    credit_model = CreditModel(db)
    credits = await credit_model.get_all(active_only=active_only)
    return [CreditResponse(**credit) for credit in credits]


@router.get("/summary")
async def get_credit_summary(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Get overall credit summary"""
    credit_model = CreditModel(db)
    return await credit_model.get_summary()


@router.get("/upcoming-due")
async def get_upcoming_due_dates(
    days: int = 30,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[dict]:
    """Get credits with upcoming due dates within specified days"""
    credit_model = CreditModel(db)
    return await credit_model.get_upcoming_due_dates(days)


@router.get("/{uid}", response_model=CreditResponse)
async def get_credit(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CreditResponse:
    """Get a specific credit by UID"""
    credit_model = CreditModel(db)
    credit = await credit_model.get_by_uid(uid)
    if not credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credit with UID {uid} not found"
        )
    return CreditResponse(**credit)


@router.patch("/{uid}", response_model=CreditResponse)
async def update_credit(
    uid: str,
    credit_data: CreditUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CreditResponse:
    """Update an existing credit"""
    credit_model = CreditModel(db)
    updated_credit = await credit_model.update(
        uid, credit_data.model_dump(exclude_unset=True)
    )
    if not updated_credit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credit with UID {uid} not found or not modified"
        )
    return CreditResponse(**updated_credit)


@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_credit(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Delete a credit"""
    credit_model = CreditModel(db)
    deleted = await credit_model.delete(uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credit with UID {uid} not found"
        )
    return {"status": "deleted", "uid": uid}


# =====================================================
# ============= PAYMENT & CHARGE OPERATIONS ===========
# =====================================================

@router.post("/{uid}/payment", status_code=status.HTTP_201_CREATED)
async def record_payment(
    uid: str,
    payment: CreditPayment,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Record a payment on credit"""
    credit_model = CreditModel(db)
    
    # Override credit_uid with path parameter
    payment_data = payment.model_dump()
    payment_data["credit_uid"] = uid
    
    try:
        result = await credit_model.record_payment(payment_data)
        return {"status": "payment_recorded", "payment": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{uid}/charge", status_code=status.HTTP_201_CREATED)
async def record_charge(
    uid: str,
    charge: CreditCharge,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Record a new charge/purchase on credit"""
    credit_model = CreditModel(db)
    
    # Override credit_uid with path parameter
    charge_data = charge.model_dump()
    charge_data["credit_uid"] = uid
    
    try:
        result = await credit_model.record_charge(charge_data)
        return {"status": "charge_recorded", "charge": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{uid}/payments")
async def get_payment_history(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[dict]:
    """Get payment history for a credit"""
    credit_model = CreditModel(db)
    return await credit_model.get_payment_history(uid)


@router.get("/{uid}/charges")
async def get_charge_history(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[dict]:
    """Get charge history for a credit"""
    credit_model = CreditModel(db)
    return await credit_model.get_charge_history(uid)