import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.integration
@pytest.mark.anyio
def test_user_signup_login_flow():
    # --- signup ---
    r = client.post("/users/signup", json={"username": "alice", "password": "secret", "name": "Alice"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"
    user_id = data["_id"]

    # --- duplicate signup ---
    r_dup = client.post("/users/signup", json={"username": "alice", "password": "secret2", "name": "Alice2"})
    assert r_dup.status_code == 409  # Conflict

    # --- login ---
    r2 = client.post("/users/login", params={"username": "alice", "password": "secret"})
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- invalid login ---
    r_invalid = client.post("/users/login", params={"username": "alice", "password": "wrong"})
    assert r_invalid.status_code == 400

    # --- get current user ---
    r3 = client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["username"] == "alice"

    # --- get current user with invalid token ---
    r_invalid_auth = client.get("/users/me", headers={"Authorization": "Bearer wrongtoken"})
    assert r_invalid_auth.status_code == 404

    # --- update user ---
    update_payload = {"name": "Alice Updated", "allergen_preferences": ["peanuts"]}
    r4 = client.put("/users/me", headers=headers, json=update_payload)
    assert r4.status_code == 200
    data_update = r4.json()
    assert data_update["name"] == "Alice Updated"
    assert data_update.get("allergen_preferences") == ["peanuts"]

    # --- update with no fields (should return 400) ---
    r_empty_update = client.put("/users/me", headers=headers, json={})
    assert r_empty_update.status_code == 422

    # --- get user by id ---
    r5 = client.get(f"/users/{user_id}")
    assert r5.status_code == 200
    assert r5.json()["username"] == "alice"

    # --- get user by username ---
    r6 = client.get("/users/alice")
    assert r6.status_code == 200
    assert r6.json()["_id"] == user_id

    # --- delete user ---
    r7 = client.delete("/users/me", headers=headers)
    assert r7.status_code == 200
    assert r7.json()["detail"] == "deleted"

    # --- get deleted user ---
    r8 = client.get(f"/users/{user_id}")
    assert r8.status_code == 404


@pytest.mark.integration
@pytest.mark.anyio
def test_signup_password_length_limits():
    # --- too short password ---
    r = client.post("/users/signup", json={"username": "bob", "password": "ab", "name": "Bob"})
    assert r.status_code == 422

    # --- valid max length password ---
    long_pwd = "a" * 72
    r2 = client.post("/users/signup", json={"username": "bob", "password": long_pwd, "name": "Bob"})
    assert r2.status_code == 200
    assert r2.json()["username"] == "bob"
