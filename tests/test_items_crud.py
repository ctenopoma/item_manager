def test_create_item(client, admin_token_headers):
    response = client.post(
        "/api/v1/items/", 
        json={"name": "PC1", "management_code": "PC-001", "category": "PC"},
        headers=admin_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "PC1"
    assert data["status"] == "available"

def test_create_item_user_fail(client, user_token_headers):
    response = client.post(
        "/api/v1/items/", 
        json={"name": "PC2", "management_code": "PC-002"},
        headers=user_token_headers
    )
    assert response.status_code == 403

def test_read_items(client, admin_token_headers):
    # Create one
    client.post("/api/v1/items/", json={"name": "PC1", "management_code": "PC-001"}, headers=admin_token_headers)
    response = client.get("/api/v1/items/", headers=admin_token_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
