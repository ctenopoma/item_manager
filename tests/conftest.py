import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from inventory_app.main import app
from inventory_app.database import Base, get_db
from inventory_app import models
from inventory_app.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token_headers(client):
    db = TestingSessionLocal()
    admin = models.User(
        username="admin", 
        hashed_password=get_password_hash("admin"), 
        role="admin",
        display_name="Admin User"
    )
    db.add(admin)
    db.commit()
    db.close()
    
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_token_headers(client):
    db = TestingSessionLocal()
    user = models.User(
        username="user", 
        hashed_password=get_password_hash("user"), 
        role="user",
        display_name="Normal User"
    )
    db.add(user)
    db.commit()
    db.close()
    
    response = client.post("/token", data={"username": "user", "password": "user"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user2_token_headers(client):
    db = TestingSessionLocal()
    user = models.User(
        username="user2", 
        hashed_password=get_password_hash("user2"), 
        role="user",
        display_name="Normal User 2"
    )
    db.add(user)
    db.commit()
    db.close()
    
    response = client.post("/token", data={"username": "user2", "password": "user2"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
