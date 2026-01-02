"""Item Manager アプリケーションのデータベースモデル.

このモジュールは、User, Item, Log, NotificationSettings, EmailTemplate など、
データベースインタラクションに使用される SQLAlchemy モデルを定義します.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class Role(str, enum.Enum):
    """ユーザーロールの列挙型."""
    admin = "admin"
    user = "user"

class ItemStatus(str, enum.Enum):
    """備品ステータスの列挙型."""
    available = "available"
    borrowed = "borrowed"
    broken = "broken"

class LogAction(str, enum.Enum):
    """ログアクションの列挙型."""
    borrow = "borrow"
    return_ = "return"

class User(Base):
    """システム内のユーザーを表します.

    Attributes:
        id (int): プライマリキー.
        username (str): 一意のユーザー名.
        hashed_password (str): ハッシュ化されたパスワード.
        display_name (str): ユーザーの表示名.
        employee_id (str, optional): 社員ID.
        email (str, optional): メールアドレス.
        department (str, optional): 部署名.
        role (str): ユーザーロール (admin または user).
        is_active (bool): ユーザーが有効かどうか.
        items (list[Item]): ユーザーが所有している備品のリスト.
        logs (list[Log]): ユーザーに関連するログのリスト.
    """
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
    """インベントリ内の備品を表します.

    Attributes:
        id (int): プライマリキー.
        name (str): 備品名.
        management_code (str): 備品の一意な管理コード.
        category (str): 備品のカテゴリ.
        status (str): 備品の現在のステータス (available, borrowed, broken).
        owner_id (int, optional): 現在備品を借りているユーザーのID.
        due_date (date, optional): 返却予定日.
        accessories (list): 備品に関連する付属品のリスト.
        is_fixed_asset (bool): 固定資産かどうか.
        lending_reason (str, optional): 貸出理由.
        lending_location (str, optional): 貸出場所.
        owner (User): 現在備品を借りているユーザー.
        logs (list[Log]): 備品に関連するログのリスト.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    management_code = Column(String, unique=True, index=True)
    category = Column(String)
    status = Column(String, default=ItemStatus.available.value)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    due_date = Column(Date, nullable=True)
    accessories = Column(JSON, default=[])
    is_fixed_asset = Column(Boolean, default=False)
    lending_reason = Column(String, nullable=True)
    lending_location = Column(String, nullable=True)

    owner = relationship("User", back_populates="items")
    logs = relationship("Log", back_populates="item")

class Log(Base):
    """備品のアクションログエントリを表します.

    Attributes:
        id (int): プライマリキー.
        item_id (int): 関連する備品のID.
        user_id (int): 関連するユーザーのID.
        action (str): 実行されたアクション (borrow, return).
        created_at (datetime): アクションのタイムスタンプ.
        item (Item): ログに関連する備品.
        user (User): ログに関連するユーザー.
    """
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="logs")
    user = relationship("User", back_populates="logs")

class NotificationSettings(Base):
    """システムの通知設定を表します.

    Attributes:
        id (int): プライマリキー.
        n_days_before (int): 返却予定日の何日前にリマインダーを送信するか.
        m_days_overdue (int): 返却予定日を何日過ぎたら督促を送信するか.
        smtp_server (str): SMTPサーバーのアドレス.
        smtp_port (int): SMTPサーバーのポート.
        smtp_username (str, optional): SMTPユーザー名.
        smtp_password (str, optional): SMTPパスワード.
        sender_email (str, optional): 送信者のメールアドレス.
    """
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    n_days_before = Column(Integer, default=3)
    m_days_overdue = Column(Integer, default=7)
    smtp_server = Column(String, default="smtp.gmail.com")
    smtp_port = Column(Integer, default=587)
    smtp_username = Column(String, nullable=True)
    smtp_password = Column(String, nullable=True)
    sender_email = Column(String, nullable=True)

class EmailTemplate(Base):
    """メールテンプレートを表します.

    Attributes:
        id (int): プライマリキー.
        name (str): テンプレート名 (例: 'reminder', 'due_today', 'overdue').
        subject (str): メールの件名.
        body (str): メールの本文.
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., 'reminder', 'due_today', 'overdue'
    subject = Column(String)
    body = Column(String) # Text with placeholders
