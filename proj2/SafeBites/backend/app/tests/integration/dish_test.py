import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.mark.integration
@pytest.mark.anyio
def test_dish_create_list_safe_flag(client):
    u = client.post("/users/signup", json={"username":"u_safe","password":"pswd","name":"U","allergen_preferences":["peanuts"]})
    uid = u.json()["_id"]

    d1 = client.post("/dishes/R1", json={"name":"Peanut Curry","restaurant":"R1","price":10,"explicit_allergens":["peanuts"]})
    assert d1.status_code == 201
    d2 = client.post("/dishes/R1", json={"name":"Salad","restaurant":"R1","price":8,"explicit_allergens":[]})
    assert d2.status_code == 201

    res = client.get("/dishes/", params={"user_id": uid})
    assert res.status_code == 200
    arr = res.json()

    pc = next((x for x in arr if x["name"]=="Peanut Curry"), None)
    sd = next((x for x in arr if x["name"]=="Salad"), None)

    assert pc is not None and pc["safe_for_user"] is False
    assert sd is not None and sd["safe_for_user"] is True

@pytest.mark.integration
@pytest.mark.anyio
def test_get_single_dish(client):
    # Create dish
    d = client.post("/dishes/R2", json={
        "name":"Tomato Soup",
        "restaurant":"R2",
        "price":6,
        "explicit_allergens":["tomato"]
    })
    dish_id = d.json()["_id"]

    # Get dish by ID
    res = client.get(f"/dishes/{dish_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Tomato Soup"
    assert data["restaurant_id"] == "R2"
    assert data["price"] == 6
    assert "safe_for_user" in data

@pytest.mark.integration
@pytest.mark.anyio
def test_update_dish(client):
    # Create dish
    d = client.post("/dishes/R3", json={
        "name":"Veggie Burger",
        "restaurant":"R3",
        "price":12,
        "explicit_allergens":["gluten"]
    })
    dish_id = d.json()["_id"]

    # Update dish price
    res = client.put(f"/dishes/{dish_id}", json={"price":14})
    assert res.status_code == 200
    data = res.json()
    assert data["price"] == 14

@pytest.mark.integration
@pytest.mark.anyio
def test_delete_dish(client):
    # Create dish
    d = client.post("/dishes/R4", json={
        "name":"Fruit Salad",
        "restaurant":"R4",
        "price":7,
        "explicit_allergens":[]
    })
    dish_id = d.json()["_id"]

    # Delete dish
    res = client.delete(f"/dishes/{dish_id}")
    assert res.status_code == 200
    assert res.json()["detail"] == "deleted"

    # Ensure dish is gone
    get_res = client.get(f"/dishes/{dish_id}")
    assert get_res.status_code == 404

@pytest.mark.integration
@pytest.mark.anyio
def test_filter_dishes_exclude_allergens(client):
    # Create dishes
    client.post("/dishes/R5", json={
        "name":"Peanut Butter Sandwich",
        "restaurant":"R5",
        "price":5,
        "explicit_allergens":["peanuts"]
    })
    client.post("/dishes/R5", json={
        "name":"Cheese Sandwich",
        "restaurant":"R5",
        "price":5,
        "explicit_allergens":["dairy"]
    })

    # Filter out peanuts
    res = client.get("/dishes/filter", params={"exclude_allergens":"peanuts"})
    assert res.status_code == 200
    arr = res.json()
    names = [x["name"] for x in arr]
    assert "Peanut Butter Sandwich" not in names
    assert "Cheese Sandwich" in names