import pytest
from app.services import dish_service
from app.models.dish_model import DishCreate
from app.models.exception_model import BadRequestException, ConflictException, NotFoundException

def test_create_dish_validation():
    dc = DishCreate(name="", restaurant_id="R1", price=0)
    with pytest.raises(BadRequestException):
        dish_service.create_dish("R1",dc)

def test_conflict_dish(monkeypatch):
    class FakeCollection:
        def find_one(self, q):
            return {"name": "D", "restaurant_id": "R"}

    # Patch the WHOLE collection object, not just the method
    monkeypatch.setattr(dish_service.db, "dishes", FakeCollection())

    dc = DishCreate(name="D", restaurant_id="R", price=5)

    with pytest.raises(ConflictException):
        dish_service.create_dish("R",dc)

def test_get_nonexistent_dish(monkeypatch):
    monkeypatch.setattr(dish_service.db.dishes, "find_one", lambda q: None)
    with pytest.raises(NotFoundException):
        dish_service.get_dish("123123123123123123123123")

