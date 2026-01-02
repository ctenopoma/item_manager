def test_login_success(client, user_token_headers):
    # Ensure token is working
    response = client.get("/api/v1/users/me", headers=user_token_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "user"

def test_login_fail(client):
    response = client.post("/token", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401

def test_protected_route(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
