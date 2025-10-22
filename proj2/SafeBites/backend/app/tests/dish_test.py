import pytest

"""
DISH TEST CASES (CRUD + edge cases)
1. test_create_dish_success – Successfully create a dish
2. test_get_dish_by_id – Retrieve dish by ID
3. test_update_dish – Update dish details
4. test_delete_dish – Delete dish by ID
5. test_get_all_dishes – Fetch all dishes
6. test_create_dish_missing_fields – Fail when required fields missing
7. test_update_nonexistent_dish – Handle invalid dish update
8. test_delete_nonexistent_dish – Handle invalid delete gracefully
9. test_filter_dishes_by_allergen – Filter dishes by allergen safety
10. test_duplicate_dish_name – Prevent duplicate dish entry (same restaurant)
"""

@pytest.mark.asyncio
async def test_create_dish_success(client):
    """Successfully create a dish"""
    payload = {
        "name": "Paneer Butter Masala",
        "price": 12.99,
        "ingredients": ["paneer", "butter", "cream"],
        "restaurant_id": "resto001",
        "allergens": ["dairy"]
    }
    res = await client.post("/dishes/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Paneer Butter Masala"
    assert "dairy" in data["allergens"]


@pytest.mark.asyncio
async def test_get_dish_by_id(client):
    """Retrieve dish by ID"""
    # Create dish
    create = await client.post("/dishes/", json={
        "name": "Veg Biryani",
        "price": 9.99,
        "ingredients": ["rice", "spices", "vegetables"],
        "restaurant_id": "resto002",
        "allergens": []
    })
    assert create.status_code == 200
    dish_id = create.json()["_id"]

    # Fetch
    res = await client.get(f"/dishes/{dish_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Veg Biryani"


@pytest.mark.asyncio
async def test_update_dish(client):
    """Update dish details"""
    create = await client.post("/dishes/", json={
        "name": "Mango Lassi",
        "price": 4.50,
        "ingredients": ["mango", "yogurt"],
        "restaurant_id": "resto003",
        "allergens": ["dairy"]
    })
    dish_id = create.json()["_id"]

    update = await client.put(f"/dishes/{dish_id}", json={"price": 5.00})
    assert update.status_code == 200
    assert update.json()["price"] == 5.00


@pytest.mark.asyncio
async def test_delete_dish(client):
    """Delete dish by ID"""
    create = await client.post("/dishes/", json={
        "name": "Chole Bhature",
        "price": 11.0,
        "ingredients": ["chickpeas", "flour"],
        "restaurant_id": "resto004",
        "allergens": ["gluten"]
    })
    dish_id = create.json()["_id"]

    res = await client.delete(f"/dishes/{dish_id}")
    assert res.status_code in [200, 204]


@pytest.mark.asyncio
async def test_get_all_dishes(client):
    """Fetch all dishes"""
    await client.post("/dishes/", json={
        "name": "Dal Tadka",
        "price": 8.50,
        "ingredients": ["lentils", "ghee"],
        "restaurant_id": "resto005",
        "allergens": ["dairy"]
    })
    res = await client.get("/dishes/")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_create_dish_missing_fields(client):
    """Creating dish with missing fields should fail"""
    res = await client.post("/dishes/", json={"price": 10})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_update_nonexistent_dish(client):
    """Updating non-existent dish should return 404"""
    res = await client.put("/dishes/507f1f77bcf86cd799439011", json={"price": 99})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_dish(client):
    """Deleting non-existent dish should return 404"""
    res = await client.delete("/dishes/507f1f77bcf86cd799439022")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_filter_dishes_by_allergen(client):
    """Filter dishes by allergen safety"""
    # Create dishes with allergens
    await client.post("/dishes/", json={
        "name": "Peanut Curry",
        "price": 12,
        "ingredients": ["peanuts", "spices"],
        "restaurant_id": "resto007",
        "allergens": ["peanuts"]
    })
    await client.post("/dishes/", json={
        "name": "Plain Rice",
        "price": 5,
        "ingredients": ["rice"],
        "restaurant_id": "resto008",
        "allergens": []
    })

    # Filter safe dishes
    res = await client.get("/dishes/filter?exclude_allergens=peanuts")
    assert res.status_code == 200
    safe_dishes = res.json()
    assert all("peanuts" not in d.get("allergens", []) for d in safe_dishes)


@pytest.mark.asyncio
async def test_duplicate_dish_name(client):
    """Prevent duplicate dish (same restaurant, same name)"""
    payload = {
        "name": "Masala Dosa",
        "price": 7.99,
        "ingredients": ["rice", "potato", "spices"],
        "restaurant_id": "resto009",
        "allergens": []
    }
    await client.post("/dishes/", json=payload)
    res = await client.post("/dishes/", json=payload)
    assert res.status_code in [400, 409]
