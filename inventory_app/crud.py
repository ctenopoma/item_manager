"""Item Manager アプリケーションの CRUD 操作.

このモジュールには、データベース内のユーザーと備品の作成 (Create)、
読み取り (Read)、更新 (Update)、削除 (Delete) を行うための関数が含まれています.
"""

from sqlalchemy.orm import Session
from . import models, schemas, security
from datetime import date
from sqlalchemy.exc import IntegrityError

def get_user(db: Session, user_id: int):
    """IDでユーザーを取得します.

    Args:
        db (Session): データベースセッション.
        user_id (int): 取得するユーザーのID.
    
    Returns:
        models.User: ユーザーオブジェクト. 見つからない場合は None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """ユーザー名でユーザーを取得します.

    Args:
        db (Session): データベースセッション.
        username (str): 検索するユーザー名.
    
    Returns:
        models.User: ユーザーオブジェクト. 見つからない場合は None.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """ユーザーのリストを取得します.

    Args:
        db (Session): データベースセッション.
        skip (int): スキップするレコード数 (ページネーション用).
        limit (int): 取得する最大レコード数.
    
    Returns:
        list[models.User]: ユーザーオブジェクトのリスト.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """新規ユーザーを作成します.

    Args:
        db (Session): データベースセッション.
        user (schemas.UserCreate): ユーザー作成データ.
    
    Returns:
        models.User: 作成されたユーザーオブジェクト.
    """
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
    """備品のリストを取得します.

    Args:
        db (Session): データベースセッション.
        skip (int): スキップするレコード数.
        limit (int): 取得する最大レコード数.
    
    Returns:
        list[models.Item]: 備品オブジェクトのリスト.
    """
    return db.query(models.Item).offset(skip).limit(limit).all()

def get_item(db: Session, item_id: int):
    """IDで備品を取得します.

    Args:
        db (Session): データベースセッション.
        item_id (int): 取得する備品のID.
    
    Returns:
        models.Item: 備品オブジェクト. 見つからない場合は None.
    """
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def create_item(db: Session, item: schemas.ItemCreate):
    """新規備品を作成します.

    Args:
        db (Session): データベースセッション.
        item (schemas.ItemCreate): 備品作成データ.
    
    Returns:
        models.Item: 作成された備品オブジェクト.
    """
    db_item = models.Item(**item.dict(), status=models.ItemStatus.available.value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    """IDで備品を削除します.

    Args:
        db (Session): データベースセッション.
        item_id (int): 削除する備品のID.
    
    Returns:
        bool: 削除された場合は True, 備品が見つからない場合は False.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def borrow_item(db: Session, item_id: int, user_id: int, due_date: date, lending_reason: str = None, lending_location: str = None):
    """備品を貸し出します.

    Args:
        db (Session): データベースセッション.
        item_id (int): 貸し出す備品のID.
        user_id (int): 備品を借りるユーザーのID.
        due_date (date): 返却予定日.
        lending_reason (str, optional): 貸出理由.
        lending_location (str, optional): 貸出場所.
    
    Returns:
        models.Item: 更新された備品オブジェクト. 見つからない場合は None.
    
    Raises:
        ValueError: 備品が利用可能でない場合.
    """
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
    """備品を返却します.

    Args:
        db (Session): データベースセッション.
        item_id (int): 返却する備品のID.
        user_id (int): 備品を返却するユーザーのID.
        force (bool): Trueの場合、所有者チェックをバイパスします (管理者強制返却).
    
    Returns:
        models.Item: 更新された備品オブジェクト. 見つからない場合は None.
    
    Raises:
        ValueError: 備品が貸出中でない場合、またはユーザーが借用者でない場合 (force=Falseのとき).
    """
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
