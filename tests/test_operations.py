import datetime
from inventory_app import models

def test_borrow_item(client, admin_token_headers, user_token_headers):
    # Create item
    client.post("/api/v1/items/", json={"name": "PC1", "management_code": "PC-001"}, headers=admin_token_headers)
    item_id = client.get("/api/v1/items/", headers=admin_token_headers).json()[0]["id"]
    
    # Borrow
    param = {"due_date": (datetime.date.today() + datetime.timedelta(days=7)).isoformat()}
    response = client.post(f"/api/v1/items/{item_id}/borrow", json=param, headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "borrowed"
    assert data["due_date"] == param["due_date"]
    
    # Borrow again fail
    response = client.post(f"/api/v1/items/{item_id}/borrow", json=param, headers=user_token_headers)
    assert response.status_code == 400

def test_return_item(client, admin_token_headers, user_token_headers):
    # Setup: Create and borrow
    client.post("/api/v1/items/", json={"name": "PCReturn", "management_code": "PC-RET"}, headers=admin_token_headers)
    # Fetch specifically this item to be safe against previous tests persistence (though conftest clears DB)
    items = client.get("/api/v1/items/", headers=admin_token_headers).json()
    item_id = [i["id"] for i in items if i["name"] == "PCReturn"][0]
    
    param = {"due_date": "2025-12-31"}
    client.post(f"/api/v1/items/{item_id}/borrow", json=param, headers=user_token_headers)
    
    # Return
    response = client.post(f"/api/v1/items/{item_id}/return", headers=user_token_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "available"

def test_return_other_user_fail(client, admin_token_headers, user_token_headers, user2_token_headers):
    # Setup: Create and borrow by user1
    client.post("/api/v1/items/", json={"name": "PC2", "management_code": "PC-002"}, headers=admin_token_headers)
    items = client.get("/api/v1/items/", headers=admin_token_headers).json()
    item_id = [i["id"] for i in items if i["name"] == "PC2"][0]
    
    param = {"due_date": "2025-12-31"}
    client.post(f"/api/v1/items/{item_id}/borrow", json=param, headers=user_token_headers)
    
    # Try return by user2
    response = client.post(f"/api/v1/items/{item_id}/return", headers=user2_token_headers)
    assert response.status_code == 403

def test_admin_force_return(client, admin_token_headers, user_token_headers):
    # Setup: Create and borrow by user1
    client.post("/api/v1/items/", json={"name": "PCForce", "management_code": "PC-FORCE"}, headers=admin_token_headers)
    items = client.get("/api/v1/items/", headers=admin_token_headers).json()
    item_id = [i["id"] for i in items if i["name"] == "PCForce"][0]
    
    param = {"due_date": "2025-12-31"}
    client.post(f"/api/v1/items/{item_id}/borrow", json=param, headers=user_token_headers)
    
    # Force return by admin
    response = client.post(f"/api/v1/items/{item_id}/return", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["status"] == models.ItemStatus.available.value

def test_growi_status_endpoint(client, admin_token_headers, user_token_headers):
    # Setup items
    client.post("/api/v1/items/", json={"name": "PC_Growi", "management_code": "PC-G"}, headers=admin_token_headers)
    
    # Check Endpoint
    response = client.get("/api/v1/items/status") # Should be public or at least accessible? 
    # Wait, original design 4.4 says "Security: Growiサーバーからのアクセスを許可". 
    # Internal design didn't specify auth for this endpoint explicitly in table 4.2? 
    # Implementation in growi.py used `db: Session = Depends(database.get_db)`.
    # `database.get_db` does not require auth.
    # So it is public.
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(i["name"] == "PC_Growi" for i in data)
