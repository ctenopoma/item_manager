from sqladmin import ModelView
from .models import User, Item, Log

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.display_name, User.employee_id, User.email, User.department, User.role, User.is_active]
    column_searchable_list = [User.username, User.display_name, User.employee_id, User.email]
    column_sortable_list = [User.id, User.username]
    icon = "fa-solid fa-user"

class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.name, Item.management_code, Item.status, Item.owner_id]
    column_searchable_list = [Item.name, Item.management_code]
    column_sortable_list = [Item.id, Item.name, Item.status]
    icon = "fa-solid fa-box"

class LogAdmin(ModelView, model=Log):
    column_list = [Log.id, Log.item_id, Log.user_id, Log.action, Log.created_at]
    column_sortable_list = [Log.created_at]
    icon = "fa-solid fa-history"
    can_create = False
    can_edit = False
    can_delete = False
