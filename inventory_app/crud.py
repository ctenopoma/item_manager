from sqlalchemy.orm import Session
from . import models, schemas, security
from datetime import date
from sqlalchemy.exc import IntegrityError

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        display_name=user.display_name,
        employee_id=user.employee_id,
        email=user.email,
        department=user.department,
        role=models.Role.user.value # Default to user
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict(), status=models.ItemStatus.available.value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def borrow_item(db: Session, item_id: int, user_id: int, due_date: date, lending_reason: str = None, lending_location: str = None):
    # Lock the row? For SQLite it's less critical but good practice.
    # Here we just fetch and check.
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        return None
    
    if item.status != models.ItemStatus.available.value:
        raise ValueError("Item is not available")
    
    item.status = models.ItemStatus.borrowed.value
    item.owner_id = user_id
    item.due_date = due_date
    item.lending_reason = lending_reason
    item.lending_location = lending_location
    
    log = models.Log(item_id=item_id, user_id=user_id, action=models.LogAction.borrow.value)
    db.add(log)
    
    db.commit()
    db.refresh(item)
    return item

def return_item(db: Session, item_id: int, user_id: int, force: bool = False):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        return None
    
    if item.status != models.ItemStatus.borrowed.value:
        raise ValueError("Item is not borrowed")
    
    if not force and item.owner_id != user_id:
         raise ValueError("User is not the borrower")
    
    item.status = models.ItemStatus.available.value
    item.owner_id = None
    item.due_date = None
    item.lending_reason = None
    item.lending_location = None
    
    log = models.Log(item_id=item_id, user_id=user_id, action=models.LogAction.return_.value)
    db.add(log)
    
    db.commit()
    db.refresh(item)
    return item
