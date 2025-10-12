import pytest

@pytest.mark.asyncio
async def test_signup_and_login_and_profile(client):
    # create user
    r = await client.post("/users/signup", json={
        "name":"Alice",
        "email":"alice@test.com",
        "password":"secret",
        "allergen_preferences":["peanuts"]
    })
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "alice@test.com"
    uid = data["_id"]

    # login
    r2 = await client.post("/users/login", params={"email":"alice@test.com","password":"secret"})
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    assert token

    # get me
    headers = {"Authorization": f"Bearer {token}"}
    r3 = await client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["email"] == "alice@test.com"

    # update me (name)
    r4 = await client.put("/users/me", json={"name":"Alice Updated"}, headers=headers)
    assert r4.status_code == 200
    assert r4.json()["name"] == "Alice Updated"

    # delete me
    r5 = await client.delete("/users/me", headers=headers)
    assert r5.status_code == 200 or r5.status_code == 204
