# backend/app/tests/integration/test_dish_integration.py
import pytest

@pytest.mark.integration
@pytest.mark.anyio
def test_dish_create_list_safe_flag(client):
    # create user
    u = client.post("/users/signup", json={"username":"u_safe","password":"pswd","name":"U","allergen_preferences":["peanuts"]})
    print(u.status_code, u.json())
    uid = u.json()["_id"] 

    # create dishes
    d1 = client.post("/dishes/", json={"name":"Peanut Curry","restaurant":"R1","price":10,"explicit_allergens":["peanuts"]})
    assert d1.status_code == 201
    d2 = client.post("/dishes/", json={"name":"Salad","restaurant":"R1","price":8,"explicit_allergens":[]})
    assert d2.status_code == 201

    # list dishes with user_id -> safe_for_user flag present
    res = client.get("/dishes/", params={"user_id": uid})
    assert res.status_code == 200
    arr = res.json()
    # find peanut curry
    pc = next((x for x in arr if x["name"]=="Peanut Curry"), None)
    sd = next((x for x in arr if x["name"]=="Salad"), None)
    assert pc is not None and pc["safe_for_user"] is False
    assert sd is not None and (sd["safe_for_user"] is True or sd["safe_for_user"] == True)
