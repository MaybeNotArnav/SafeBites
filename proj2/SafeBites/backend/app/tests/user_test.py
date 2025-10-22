import pytest

"""
USER TEST CASES (CRUD + edge cases)
1. test_create_user_success – Create a user successfully
2. test_get_user_by_id – Retrieve a user by ID
3. test_update_user_profile – Update user profile
4. test_delete_user – Delete user
5. test_duplicate_user_signup – Prevent duplicate signup
6. test_create_user_missing_fields – Fail if required fields missing
7. test_login_with_invalid_credentials – Invalid login attempt
8. test_get_nonexistent_user – Handle non-existent user fetch
9. test_update_user_partial_data – Partial updates allowed
10. test_delete_nonexistent_user – Handle invalid delete gracefully
"""

@pytest.mark.asyncio
async def test_signup_and_login_and_profile(client):
    """End-to-end: signup → login → fetch profile → update → delete"""
    # Create user
    r = await client.post("/users/signup", json={
        "name": "Alice",
        "email": "alice@test.com",
        "password": "secret",
        "allergen_preferences": ["peanuts"]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "alice@test.com"
    uid = data["_id"]

    # Login
    r2 = await client.post("/users/login", params={
        "email": "alice@test.com",
        "password": "secret"
    })
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    assert token

    # Fetch user profile
    headers = {"Authorization": f"Bearer {token}"}
    r3 = await client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["email"] == "alice@test.com"

    # Update user profile
    r4 = await client.put("/users/me", json={"name": "Alice Updated"}, headers=headers)
    assert r4.status_code == 200
    assert r4.json()["name"] == "Alice Updated"

    # Delete user
    r5 = await client.delete("/users/me", headers=headers)
    assert r5.status_code in [200, 204]


@pytest.mark.asyncio
async def test_create_user_missing_fields(client):
    """Creating user with missing required fields should fail"""
    response = await client.post("/users/signup", json={"name": "userX"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(client):
    """Login attempt with wrong password should fail"""
    # Create valid user
    await client.post("/users/signup", json={
        "name": "Bob",
        "email": "bob@test.com",
        "password": "pass123"
    })

    # Wrong password
    response = await client.post("/users/login", params={
        "email": "bob@test.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_nonexistent_user(client):
    """Fetching a user that doesn't exist should return 404"""
    response = await client.get("/users/507f1f77bcf86cd799439011")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user_partial_data(client):
    """Partial update of user profile should succeed"""
    # Create user
    r = await client.post("/users/signup", json={
        "name": "Charlie",
        "email": "charlie@test.com",
        "password": "abc123"
    })
    assert r.status_code == 200
    uid = r.json()["_id"]

    # Update partial field
    response = await client.put(f"/users/{uid}", json={"name": "CharlieUpdated"})
    assert response.status_code == 200
    assert response.json()["name"] == "CharlieUpdated"


@pytest.mark.asyncio
async def test_delete_nonexistent_user(client):
    """Deleting non-existent user should return 404"""
    response = await client.delete("/users/507f1f77bcf86cd799439022")
    assert response.status_code == 404
