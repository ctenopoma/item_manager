from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from .. import database, schemas, crud, models
from .auth import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/api/v1/items",
    tags=["items"],
)

@router.get("/status", response_model=List[schemas.GrowiItem])
def get_items_status(db: Session = Depends(database.get_db)):
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
            name=item.name,
            management_code=item.management_code,
            status=item.status,
            owner_name=owner_name,
            due_date=item.due_date,
            is_overdue=is_overdue,
            is_fixed_asset=item.is_fixed_asset or False,
            accessories=item.accessories or []
        ))
    return result

@router.get("/", response_model=List[schemas.ItemResponse])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_active_user)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@router.post("/", response_model=schemas.ItemResponse, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.create_item(db=db, item=item)

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_admin_user)):
    success = crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None

class BorrowRequest(schemas.BaseModel):
    due_date: schemas.date

@router.post("/{item_id}/borrow", response_model=schemas.ItemResponse)
def borrow_item(
    item_id: int, 
    borrow_request: schemas.ItemUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if not borrow_request.due_date:
        raise HTTPException(status_code=400, detail="Due date is required")
        
    try:
        item = crud.borrow_item(db=db, item_id=item_id, user_id=current_user.id, due_date=borrow_request.due_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/{item_id}/return", response_model=schemas.ItemResponse)
def return_item(item_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_active_user)):
    is_admin = current_user.role == models.Role.admin.value
    
    try:
        item = crud.return_item(db=db, item_id=item_id, user_id=current_user.id, force=is_admin)
    except ValueError as e:
        # Internal design C-4 requires 403 Forbidden when trying to return another's item
        if "User is not the borrower" in str(e):
             raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
