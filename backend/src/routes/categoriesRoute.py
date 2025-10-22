from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from ..schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)
from ..models.categories import CategoryModel
from ..database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Create a new category"""
    category_model = CategoryModel(db)
    result = await category_model.create(category.model_dump())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create category"
        )
    return CategoryResponse(**result)


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> List[CategoryResponse]:
    """Get all categories"""
    category_model = CategoryModel(db)
    categories = await category_model.get_all()
    return [CategoryResponse(**cat) for cat in categories]



async def fetch_children(db, parent_uid: str):
    """Recursively fetch children categories"""
    children_cursor = db.categories.find({"parent_uid": parent_uid})
    children = []
    async for child in children_cursor:
        child_dict = dict(child)
        child_dict["children"] = await fetch_children(db, child_dict["uid"])
        children.append(child_dict)
    return children


@router.get("/{uid}", response_model=CategoryResponse)
async def get_category(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Get a specific category by UID"""
    category_model = CategoryModel(db)
    category = await category_model.get_by_uid(uid)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with UID {uid} not found"
        )
    category_dict = dict(category)
    category_dict["children"] = await fetch_children(db, uid)
    return CategoryResponse(**category_dict)

@router.patch("/{uid}", response_model=CategoryResponse)
async def update_category(
    uid: str,
    cat_data: CategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Update an existing category"""
    category_model = CategoryModel(db)
    updated_category = await category_model.update(uid, cat_data.model_dump(exclude_unset=True))
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with UID {uid} not found or not modified"
        )
    return CategoryResponse(**updated_category)

@router.delete("/{uid}", status_code=status.HTTP_200_OK)
async def delete_category(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Delete a category"""
    category_model = CategoryModel(db)
    deleted = await category_model.delete(uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with UID {uid} not found"
        )
    return {"status": "deleted", "uid": uid}

