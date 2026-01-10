"""備品操作用 API ルーター.

このモジュールは、備品のリスト取得、作成、削除、貸出、返却など、
備品に関連するエンドポイントを処理します.
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, database, models, schemas
from .auth import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/api/v1/items",
    tags=["items"],
)

@router.get("/status", response_model=List[schemas.GrowiItem])
def get_items_status(db: Session = Depends(database.get_db)):
    """Growi 連携用にフォーマットされたすべての備品ステータスを取得します.
    
    このエンドポイントは、期限切れステータスと所有者の表示名が計算された備品を返します.
    """
    # This endpoint logic was moved from routers/growi.py
    items = crud.get_items(db, skip=0, limit=1000)
    result = []
    today = date.today()
    
    for item in items:
        is_overdue = False
        if item.status == models.ItemStatus.borrowed.value and item.due_date:
            if today > item.due_date:
                is_overdue = True
                
        owner_name = None
        if item.owner:
            owner_name = item.owner.display_name
            
        result.append(schemas.GrowiItem(
            id=item.id,
            name=item.name,
            management_code=item.management_code,
            status=item.status,
            owner_name=owner_name,
            due_date=item.due_date,
            is_overdue=is_overdue,
            is_fixed_asset=item.is_fixed_asset or False,
            accessories=item.accessories or [],
            lending_reason=item.lending_reason,
            lending_location=item.lending_location
        ))
    return result

@router.get("/", response_model=List[schemas.ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_active_user)):
    """備品を取得します.
    
    Args:
        skip (int): スキップする備品数.
        limit (int): 取得する備品の上限数.
    """
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=schemas.ItemResponse, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_admin_user)):
    """新規備品を作成します. 管理者ユーザーのみアクセス可能です."""
    return crud.create_item(db=db, item=item)

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_admin_user)):
    """備品を削除します. 管理者ユーザーのみアクセス可能です."""
    success = crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

class UnauthenticatedBorrowRequest(schemas.BaseModel):
    """貸出リクエスト用スキーマ."""
    username: str
    due_date: schemas.date
    lending_reason: schemas.Optional[str] = None
    lending_location: schemas.Optional[str] = None

@router.post("/{item_id}/borrow", response_model=schemas.ItemResponse)
def borrow_item(
    item_id: int, 
    borrow_request: UnauthenticatedBorrowRequest,
    db: Session = Depends(database.get_db)
):
    """備品を貸し出します.
    
    ユーザー名を提供することで、認証なしで貸出を行うことができます.
    """
    # Lookup user by username
    user = crud.get_user_by_username(db, username=borrow_request.username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not borrow_request.due_date:
        raise HTTPException(status_code=400, detail="Due date is required")
        
    try:
        item = crud.borrow_item(
            db=db, 
            item_id=item_id, 
            user_id=user.id, 
            due_date=borrow_request.due_date,
            lending_reason=borrow_request.lending_reason,
            lending_location=borrow_request.lending_location
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/{item_id}/return", response_model=schemas.ItemResponse)
def return_item(item_id: int, db: Session = Depends(database.get_db)):
    """借りている備品を返却します."""
    # Retrieve the item to find the current borrower (to log the action correctly)
    item = crud.get_item(db, item_id)
    if not item:
         raise HTTPException(status_code=404, detail="Item not found")

    user_id = item.owner_id
    if not user_id:
        # If no owner, maybe it's already returned or inconsistent.
        # Check status check inside crud.return_item will handle "not borrowed" error.
        # But we need a user_id for logging. Use 1 (Admin/System) or handle gracefully?
        # crud.return_item requires user_id.
        # If we can't identify, let's try to proceed, maybe crud throws error.
        # Let's assume user_id=0 or 1 if None.
        user_id = 1 # Fallback to admin/first user for log if somehow owner_id is missing

    try:
        # force=True allows return without checking if "current_user" matches "owner_id"
        # Since we don't have current_user, we just trust the action.
        item = crud.return_item(db=db, item_id=item_id, user_id=user_id, force=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return item
