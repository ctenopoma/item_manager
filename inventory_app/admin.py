from sqladmin import ModelView
from .models import User, Item, Log, NotificationSettings, EmailTemplate

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.display_name, User.employee_id, User.email, User.department, User.role, User.is_active]
    column_details_list = [User.id, User.username, User.display_name, User.employee_id, User.email, User.department, User.role, User.is_active]
    form_excluded_columns = ["items", "logs"]
    column_searchable_list = [User.username, User.display_name, User.employee_id, User.email]
    column_sortable_list = [User.id, User.username]
    icon = "fa-solid fa-user"

class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.name, Item.management_code, Item.status, Item.is_fixed_asset, "owner", Item.due_date, Item.lending_reason, Item.lending_location, Item.accessories]
    column_details_list = [Item.id, Item.name, Item.management_code, Item.category, Item.status, Item.is_fixed_asset, "owner", Item.due_date, Item.lending_reason, Item.lending_location, Item.accessories]
    form_excluded_columns = ["logs"]
    column_searchable_list = [Item.name, Item.management_code]
    column_sortable_list = [Item.id, Item.name, Item.status]
    icon = "fa-solid fa-box"

class LogAdmin(ModelView, model=Log):
    column_list = [Log.id, "item", "user", Log.action, Log.created_at]
    column_sortable_list = [Log.created_at]
    icon = "fa-solid fa-history"
    can_create = False
    can_edit = False
    can_delete = False

class NotificationSettingsAdmin(ModelView, model=NotificationSettings):
    column_list = [NotificationSettings.n_days_before, NotificationSettings.m_days_overdue, NotificationSettings.sender_email]
    icon = "fa-solid fa-cogs"

class EmailTemplateAdmin(ModelView, model=EmailTemplate):
    column_list = [EmailTemplate.name, EmailTemplate.subject]
    icon = "fa-solid fa-envelope"

