import pytest
from app.services import user_service
from app.models.user_model import UserCreate
from app.models.exception_model import ConflictException,BadRequestException,NotFoundException
from bson import ObjectId

def test_create_user_conflict(monkeypatch):
    class FakeCollection:
        def find_one(self, q):
            return {"_id": "x", "username": "bob"}

    monkeypatch.setattr(user_service.db, "users", FakeCollection())

    uc = UserCreate(username="bob", password="pswd", name="Bob")

    with pytest.raises(ConflictException):
        user_service.create_user(uc)


def test_password_hashing(monkeypatch):
    called = {}

    def fake_insert_one(doc):
        called['doc'] = doc
        class R:
            inserted_id = "id"
        return R()

    def fake_find_one(q):
        # When the service fetches the newly-created user by id
        if q == {"_id": "id"}:
            return {
                "_id": "id",
                "username": "u1",
                "name": "U",
                # return a hashed or placeholder password
                "password": "hashed"
            }
        return None

    monkeypatch.setattr(user_service.db.users, "insert_one", fake_insert_one)
    monkeypatch.setattr(user_service.db.users, "find_one", fake_find_one)

    uc = UserCreate(username="u1", password="pass", name="U")
    res = user_service.create_user(uc)

    # expectations
    assert "_id" in res
    assert res["username"] == "u1"
    assert called["doc"]["password"] != "pass"  # hashed

def test_update_user_no_fields(monkeypatch):
    def fake_update_one(q, u):
        pass
    monkeypatch.setattr(user_service.db.users, "update_one", fake_update_one)

    with pytest.raises(BadRequestException):
        user_service.update_user("64d2323c9f7c", {})


def test_delete_user_not_found(monkeypatch):
    class R: deleted_count = 0
    monkeypatch.setattr(user_service.db.users, "delete_one", lambda q: R())
    with pytest.raises(NotFoundException):
        user_service.delete_user("64d2323c9f7c")

# Test normal successful user creation
def test_create_user_success(monkeypatch):
    called = {}

    def fake_find_one(q):
        return None  # No existing user

    def fake_insert_one(doc):
        called['doc'] = doc
        class R:
            inserted_id = "new_id"
        return R()

    def fake_find_by_id(q):
        if q == {"_id": "new_id"}:
            return {**called['doc'], "_id": "new_id"}
        return None

    monkeypatch.setattr(user_service.db.users, "find_one", fake_find_one)
    monkeypatch.setattr(user_service.db.users, "insert_one", fake_insert_one)
    monkeypatch.setattr(user_service.db.users, "find_one", fake_find_by_id)

    uc = UserCreate(username="alice", password="mypassword", name="Alice")
    res = user_service.create_user(uc)

    assert res["_id"] == "new_id"
    assert res["username"] == "alice"
    assert called["doc"]["password"] != "mypassword"
