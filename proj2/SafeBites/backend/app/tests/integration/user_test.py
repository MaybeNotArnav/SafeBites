import pytest

@pytest.mark.integration
@pytest.mark.anyio
def test_user_signup_login_flow(client):
    r = client.post("/users/signup", json={"username":"alice","password":"secret","name":"Alice"})
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "alice"

    r2 = client.post("/users/login", params={"username":"alice","password":"secret"})
    assert r2.status_code == 200
    token = r2.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    r3 = client.get("/users/me", headers=headers)
    assert r3.status_code == 200
    assert r3.json()["username"] == "alice"
