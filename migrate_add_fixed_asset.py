from sqlalchemy import create_engine, text
from inventory_app.database import SQLALCHEMY_DATABASE_URL

def add_fixed_asset_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as connection:
        try:
            # SQLite boolean is 0 or 1
            connection.execute(text("ALTER TABLE items ADD COLUMN is_fixed_asset BOOLEAN DEFAULT 0"))
            print("Successfully added 'is_fixed_asset' column to 'items' table.")
        except Exception as e:
            print(f"Error adding column (it might already exist): {e}")

if __name__ == "__main__":
    add_fixed_asset_column()
