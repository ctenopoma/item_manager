"""ユーザー操作用 API ルーター.

このモジュールは、新規ユーザーの作成やユーザー情報の取得など、
ユーザーに関連するエンドポイントを処理します.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, database, models, schemas
from .auth import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_admin_user)):
    """新規ユーザーを作成します. 管理者ユーザーのみアクセス可能です.

    Args:
        user (schemas.UserCreate): ユーザー作成データ.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """すべてのユーザーを取得します. (認証不要)

    Args:
        skip (int): スキップするユーザー数.
        limit (int): 取得するユーザーの上限数.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/me", response_model=schemas.UserResponse)
def read_user_me(current_user: models.User = Depends(get_current_active_user)):
    """現在認証されているユーザーの情報を取得します."""
    return current_user
