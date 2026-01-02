from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class Role(str, enum.Enum):
    admin = "admin"
    user = "user"

class ItemStatus(str, enum.Enum):
    available = "available"
    borrowed = "borrowed"
    broken = "broken"

class LogAction(str, enum.Enum):
    borrow = "borrow"
    return_ = "return"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String)
    employee_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    department = Column(String, nullable=True)
    role = Column(String, default=Role.user.value)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")
    logs = relationship("Log", back_populates="user")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    management_code = Column(String, unique=True, index=True)
    category = Column(String)
    status = Column(String, default=ItemStatus.available.value)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(Date, nullable=True)

    owner = relationship("User", back_populates="items")
    logs = relationship("Log", back_populates="item")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="logs")
    user = relationship("User", back_populates="logs")
