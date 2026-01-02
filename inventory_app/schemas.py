from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    display_name: Optional[str] = None
    employee_id: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    management_code: str
    category: Optional[str] = None
    accessories: List[str] = []
    is_fixed_asset: bool = False

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[date] = None
    owner_id: Optional[int] = None

class ItemResponse(ItemBase):
    id: int
    status: str
    owner_id: Optional[int] = None
    due_date: Optional[date] = None

    class Config:
        from_attributes = True

class GrowiItem(BaseModel):
    name: str
    management_code: str
    status: str
    owner_name: Optional[str] = None
    due_date: Optional[date] = None
    is_overdue: bool
    is_fixed_asset: bool = False
    accessories: List[str] = []
