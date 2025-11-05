import pytest
from app.services import dish_service
from app.models.dish_model import DishCreate
from bson import ObjectId
from app.models.exception_model import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)


# ---------- CREATE ----------

def test_create_valid_dish(monkeypatch):
    def fake_find_one(q, *args, **kwargs):
        if "_id" in q:
            return {
                "_id": q["_id"],
                "name": "Pasta",
                "restaurant_id": "R1",
                "price": 10,
                "explicit_allergens": [],
            }
        return None

    def fake_insert_one(doc, *args, **kwargs):
        class R:
            inserted_id = "65a1b2c3d4e5f67890123456"
        return R()

    class FakeCol:
        find_one = staticmethod(fake_find_one)
        insert_one = staticmethod(fake_insert_one)

    monkeypatch.setattr(dish_service.db, "dishes", FakeCol())

    dc = DishCreate(name="Pasta", restaurant_id="R1", price=10, explicit_allergens=[])
    res = dish_service.create_dish("R1", dc)

    assert res["_id"] == "65a1b2c3d4e5f67890123456"
    assert res["name"] == "Pasta"
    assert res["safe_for_user"] is True


def test_create_conflicting_dish(monkeypatch):
    def fake_find_one(q, *args, **kwargs):
        return {"name": "Pasta"}

    class FakeCol:
        find_one = staticmethod(fake_find_one)

    monkeypatch.setattr(dish_service.db, "dishes", FakeCol())
    dc = DishCreate(name="Pasta", restaurant_id="R1", price=10, explicit_allergens=[])

    with pytest.raises(ConflictException):
        dish_service.create_dish("R1", dc)


def test_create_missing_name():
    # pydantic will catch None before service code
    with pytest.raises(Exception):
        DishCreate(name=None, restaurant_id="R1", price=10, explicit_allergens=[])


# ---------- UPDATE ----------

def test_update_existing_dish(monkeypatch):
    def fake_update_one(q, u, *args, **kwargs):
        class R:
            matched_count = 1
            modified_count = 1
        return R()

    def fake_find_one(q, *args, **kwargs):
        return {
            "_id": q["_id"],
            "name": "Burger",
            "restaurant_id": "R3",
            "price": 14,
            "explicit_allergens": ["gluten"],
        }

    class FakeCol:
        update_one = staticmethod(fake_update_one)
        find_one = staticmethod(fake_find_one)

    monkeypatch.setattr(dish_service.db, "dishes", FakeCol())

    res = dish_service.update_dish("65a1b2c3d4e5f67890123456", {"price": 14})
    assert res["price"] == 14


def test_update_no_fields():
    with pytest.raises(BadRequestException):
        dish_service.update_dish("65a1b2c3d4e5f67890123456", {})


def test_update_invalid_id():
    with pytest.raises(NotFoundException):
        dish_service.update_dish("INVALID", {"price": 10})


# ---------- DELETE ----------

def test_delete_existing_dish(monkeypatch):
    class FakeCol:
        def delete_one(self, q, *args, **kwargs):
            class R:
                deleted_count = 1
            return R()

    monkeypatch.setattr(dish_service.db, "dishes", FakeCol())
    res = dish_service.delete_dish("65a1b2c3d4e5f67890123456")

    assert res["detail"] == "deleted"


def test_delete_missing_dish(monkeypatch):
    class FakeCol:
        def delete_one(self, q, *args, **kwargs):
            class R:
                deleted_count = 0
            return R()

    monkeypatch.setattr(dish_service.db, "dishes", FakeCol())

    with pytest.raises(NotFoundException):
        dish_service.delete_dish("65a1b2c3d4e5f67890123456")


def test_delete_invalid_id():
    with pytest.raises(NotFoundException):
        dish_service.delete_dish("INVALID")
