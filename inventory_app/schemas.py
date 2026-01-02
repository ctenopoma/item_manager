"""Item Manager アプリケーションの Pydantic スキーマ.

このモジュールは、User, Item, Token, Growi 連携など、
データバリデーションとシリアライゼーションに使用される Pydantic モデルを定義します.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class Token(BaseModel):
    """JWTアクセストークンのスキーマ.

    Attributes:
        access_token (str): JWTアクセストークン文字列.
        token_type (str): トークンのタイプ (例: "bearer").
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """トークンペイロードデータのスキーマ.

    Attributes:
        username (str, optional): トークンから抽出されたユーザー名.
    """
    username: Optional[str] = None

class UserBase(BaseModel):
    """ユーザーデータの基本スキーマ.

    Attributes:
        username (str): ユーザー名.
        display_name (str, optional): ユーザーの表示名.
        employee_id (str, optional): 社員ID.
        email (str, optional): メールアドレス.
        department (str, optional): 部署名.
    """
    username: str
    display_name: Optional[str] = None
    employee_id: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    """新規ユーザー作成用スキーマ.

    Attributes:
        password (str): ユーザーのパスワード.
    """
    password: str

class UserResponse(UserBase):
    """ユーザーレスポンス用スキーマ.

    Attributes:
        id (int): ユーザーID.
        role (str): ユーザーロール.
        is_active (bool): ユーザーが有効かどうか.
    """
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    """備品データの基本スキーマ.

    Attributes:
        name (str): 備品名.
        management_code (str): 管理コード.
        category (str, optional): カテゴリ.
        accessories (list[str]): 付属品のリスト.
        is_fixed_asset (bool): 固定資産かどうか.
    """
    name: str
    management_code: str
    category: Optional[str] = None
    accessories: List[str] = []
    is_fixed_asset: bool = False

class ItemCreate(ItemBase):
    """新規備品作成用スキーマ."""
    pass

class ItemUpdate(BaseModel):
    """備品更新用スキーマ.

    Attributes:
        status (str, optional): ステータス.
        due_date (date, optional): 返却予定日.
        owner_id (int, optional): 所有者ID.
        lending_reason (str, optional): 貸出理由.
        lending_location (str, optional): 貸出場所.
    """
    status: Optional[str] = None
    due_date: Optional[date] = None
    owner_id: Optional[int] = None
    lending_reason: Optional[str] = None
    lending_location: Optional[str] = None

class ItemResponse(ItemBase):
    """備品レスポンス用スキーマ.

    Attributes:
        id (int): 備品ID.
        status (str): ステータス.
        owner_id (int, optional): 所有者ID.
        due_date (date, optional): 返却予定日.
        lending_reason (str, optional): 貸出理由.
        lending_location (str, optional): 貸出場所.
    """
    id: int
    status: str
    owner_id: Optional[int] = None
    due_date: Optional[date] = None
    lending_reason: Optional[str] = None
    lending_location: Optional[str] = None

    class Config:
        from_attributes = True

class GrowiItem(BaseModel):
    """Growi 連携表示用アイテムスキーマ.

    Attributes:
        name (str): 備品名.
        management_code (str): 管理コード.
        status (str): ステータス.
        owner_name (str, optional): 現在の所有者名.
        due_date (date, optional): 返却予定日.
        is_overdue (bool): 期限切れかどうか.
        is_fixed_asset (bool): 固定資産かどうか.
        accessories (list[str]): 付属品のリスト.
        lending_reason (str, optional): 貸出理由.
        lending_location (str, optional): 貸出場所.
    """
    name: str
    management_code: str
    status: str
    owner_name: Optional[str] = None
    due_date: Optional[date] = None
    is_overdue: bool
    is_fixed_asset: bool = False
    accessories: List[str] = []
    lending_reason: Optional[str] = None
    lending_location: Optional[str] = None
