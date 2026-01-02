from inventory_app import database, models, crud, schemas
from inventory_app.database import SessionLocal
from datetime import date, timedelta

models.Base.metadata.create_all(bind=database.engine)

db = SessionLocal()

# Cleanup
db.query(models.Log).delete()
db.query(models.Item).delete()
db.query(models.User).delete()
db.commit()

# Create Users
admin = crud.create_user(db, schemas.UserCreate(username="admin", password="adminpassword", display_name="管理者", employee_id="A0001", email="admin@example.com", department="IT"))
admin.role = "admin"
db.add(admin)

user1 = crud.create_user(db, schemas.UserCreate(username="sato", password="password", display_name="佐藤 健", employee_id="U0001", email="sato@example.com", department="Sales"))
user2 = crud.create_user(db, schemas.UserCreate(username="suzuki", password="password", display_name="鈴木 一郎", employee_id="U0002", email="suzuki@example.com", department="Engineering"))

db.commit()

# Create Items
item1 = crud.create_item(db, schemas.ItemCreate(name="MacBook Pro M3", management_code="PC-001", category="PC"))
item2 = crud.create_item(db, schemas.ItemCreate(name="Windows Test PC", management_code="PC-002", category="PC"))
item3 = crud.create_item(db, schemas.ItemCreate(name="USB-C Monitor", management_code="MON-001", category="Monitor"))
item4 = crud.create_item(db, schemas.ItemCreate(name="Design Book", management_code="BK-001", category="Book"))

# Borrow some items
# Item 1: Borrowed by Sato (Not Overdue)
crud.borrow_item(db, item1.id, user1.id, date.today() + timedelta(days=7))

# Item 2: Borrowed by Suzuki (Overdue)
# We need to hack this a bit since borrow_item sets due_date. 
# We'll use borrow_item then manually update due_date to past.
crud.borrow_item(db, item2.id, user2.id, date.today() + timedelta(days=7))
item2.due_date = date.today() - timedelta(days=1)
db.add(item2)

db.commit()
db.close()
print("Database seeded!")
