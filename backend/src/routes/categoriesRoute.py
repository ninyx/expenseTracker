from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Literal
from bson import ObjectId
from ..schemas.categories import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from ..models.categories import CategoryModel
from ..database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter(prefix="/categories", tags=["Categories"])

# =====================================================
# ============== STANDARD CRUD ENDPOINTS ==============
# =====================================================

@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category: CategoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Create a new category with budget overflow protection."""
    category_model = CategoryModel(db)
    data = category.model_dump()
    parent_uid = data.get("parent_uid")

    # ✅ Check for parent budget overflow BEFORE creating
    if parent_uid:
        parent = await category_model.get_by_uid(parent_uid)
        if not parent:
            raise HTTPException(
                status_code=404,
                detail=f"Parent category with UID '{parent_uid}' not found."
            )

        parent_budget = parent.get("budget", 0)
        if parent_budget <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Parent category '{parent.get('name')}' has no budget set."
            )

        # Get existing children and sum their budgets
        children = await category_model.get_children(parent_uid)
        total_child_budget = sum(child.get("budget", 0) for child in children)

        new_total = total_child_budget + data.get("budget", 0)
        if new_total > parent_budget:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Budget overflow: total child budgets ({new_total}) "
                    f"would exceed parent budget ({parent_budget})."
                ),
            )

    # ✅ Proceed with creation
    result = await category_model.create(data)
    if not result:
        raise HTTPException(status_code=400, detail="Could not create category")

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


@router.get("/tree", status_code=status.HTTP_200_OK)
async def get_category_tree(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Return all categories in hierarchical structure.
    Includes:
      - recursive child nesting
      - aggregated totals (spent, earned, used)
      - budget utilization ratios
      - over-budget flag
    """
    category_model = CategoryModel(db)
    all_categories = await category_model.get_all()

    if not all_categories:
        # optional: return empty list instead of 404
        return []

    # Build lookup map by UID
    category_map = {cat["uid"]: {**cat, "children": []} for cat in all_categories}
    roots = []

    # Build hierarchy
    for cat in category_map.values():
        parent_uid = cat.get("parent_uid")
        if parent_uid and parent_uid in category_map:
            category_map[parent_uid]["children"].append(cat)
        else:
            roots.append(cat)

    # Recursive aggregation
    def aggregate_totals(category):
        total_spent = category.get("total_spent", 0)
        total_earned = category.get("total_earned", 0)
        budget_used = category.get("budget_used", 0)

        for child in category.get("children", []):
            child_agg = aggregate_totals(child)
            total_spent += child_agg["total_spent"]
            total_earned += child_agg["total_earned"]
            budget_used += child_agg["budget_used"]

        category["total_spent"] = round(total_spent, 2)
        category["total_earned"] = round(total_earned, 2)
        category["budget_used"] = round(budget_used, 2)

        budget = category.get("budget", 0)
        if budget and budget > 0:
            utilization = round(budget_used / budget, 4)
            over_budget = budget_used > budget
        else:
            utilization = None
            over_budget = False

        category["budget_utilization"] = utilization
        category["is_over_budget"] = over_budget

        return {
            "total_spent": total_spent,
            "total_earned": total_earned,
            "budget_used": budget_used,
        }

    for root in roots:
        aggregate_totals(root)

    # Optional: sort children alphabetically
    def sort_children(category):
        category["children"].sort(key=lambda c: c.get("name", ""))
        for child in category["children"]:
            sort_children(child)
        return category
    

    for root in roots:
        sort_children(root)

    def convert_objectids(obj):
        """Recursively convert ObjectId to string."""
        if isinstance(obj, list):
            return [convert_objectids(i) for i in obj]
        elif isinstance(obj, dict):
            return {
                k: convert_objectids(v)
                for k, v in obj.items()
                if k != "_id"  # optionally remove Mongo's internal _id
            }
        elif isinstance(obj, ObjectId):
            return str(obj)
        return obj

    # Apply conversion before returning
    return convert_objectids(roots)
        

@router.get("/{uid}", response_model=CategoryResponse)
async def get_category(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Get a specific category by UID"""
    category_model = CategoryModel(db)
    category = await category_model.get_by_uid(uid)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with UID {uid} not found")
    category_dict = dict(category)
    category_dict["children"] = await fetch_children(db, uid)
    return CategoryResponse(**category_dict)

@router.patch("/{uid}", response_model=CategoryResponse)
async def update_category(
    uid: str,
    cat_data: CategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> CategoryResponse:
    """Update an existing category with parent/child budget validation."""
    category_model = CategoryModel(db)
    update_data = cat_data.model_dump(exclude_unset=True)

    # Check if category exists
    category = await category_model.get_by_uid(uid)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category {uid} not found or not modified"
        )

    # ✅ If updating a child budget, ensure parent limit isn't exceeded
    if "budget" in update_data and category.get("parent_uid"):
        parent = await category_model.get_by_uid(category["parent_uid"])
        if parent:
            siblings = await category_model.get_children(parent["uid"])
            total_sibling_budgets = sum(
                (update_data["budget"] if s["uid"] == uid else s.get("budget", 0))
                for s in siblings
            )
            if total_sibling_budgets > parent.get("budget", 0):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Budget overflow: Total child budgets ({total_sibling_budgets}) "
                        f"exceed parent budget ({parent.get('budget', 0)})"
                    )
                )

    updated_category = await category_model.update(uid, update_data)
    if not updated_category:
        raise HTTPException(
            status_code=404,
            detail=f"Category {uid} not found or not modified"
        )

    return CategoryResponse(**updated_category)


@router.delete("/{uid}", status_code=status.HTTP_200_OK,)
async def delete_category(
    uid: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Delete a category"""
    category_model = CategoryModel(db)
    deleted = await category_model.delete(uid)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Category {uid} not found")
    return {"status": "deleted", "uid": uid}
