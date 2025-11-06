import pytest
from bson.objectid import ObjectId
from app.services import user_service
from app.models.user_model import UserCreate, UserUpdate
from app.models.exception_model import NotFoundException, BadRequestException, ConflictException

# ----------------------
# CREATE USER
# ----------------------
def test_create_user_success(monkeypatch):
    """Creating a user successfully returns dict without password."""
    inserted = {}

    class FakeUsers:
        def find_one(self, query):
            # First call: check username
            if query.get("username") == "alice" and not inserted:
                return None
            # Fetch the inserted user
            return {**inserted, "_id": inserted.get("_id", ObjectId())}

        def insert_one(self, doc):
            inserted.update(doc)
            inserted["_id"] = ObjectId()
            class R:
                inserted_id = inserted["_id"]
            return R()

    monkeypatch.setattr(user_service.db, "users", FakeUsers())

    uc = UserCreate(username="alice", password="mypassword", name="Alice", allergen_preferences=[])
    res = user_service.create_user(uc)
    assert res["_id"] == str(inserted["_id"])
    assert res["username"] == "alice"
    assert "password" not in res

def test_create_user_conflict(monkeypatch):
    """Conflict if username already exists."""
    class FakeUsers:
        def find_one(self, query):
            return {"username": "alice"}  # existing
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    uc = UserCreate(username="alice", password="pass", name="Alice", allergen_preferences=[])
    with pytest.raises(ConflictException):
        user_service.create_user(uc)

# ----------------------
# LOGIN USER
# ----------------------
def test_login_user_success(monkeypatch):
    hashed = user_service.pwd_ctx.hash("mypassword")
    class FakeUsers:
        def find_one(self, query):
            return {"_id": ObjectId(), "username": "alice", "password": hashed}
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    res = user_service.login_user("alice", "mypassword")
    assert "access_token" in res
    assert res["token_type"] == "bearer"

def test_login_user_invalid(monkeypatch):
    class FakeUsers:
        def find_one(self, query):
            return None
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    with pytest.raises(BadRequestException):
        user_service.login_user("alice", "wrong")

# ----------------------
# GET USER
# ----------------------
def test_get_user_by_id_success(monkeypatch):
    uid = ObjectId()
    class FakeUsers:
        def find_one(self, query):
            return {"_id": uid, "username": "alice", "password": "secret"}
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    res = user_service.get_user_by_id(str(uid))
    assert res["_id"] == str(uid)
    assert res["username"] == "alice"
    assert "password" not in res

def test_get_user_by_id_not_found(monkeypatch):
    class FakeUsers:
        def find_one(self, query):
            return None
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    with pytest.raises(NotFoundException):
        user_service.get_user_by_id(str(ObjectId()))

def test_get_user_by_username_success(monkeypatch):
    class FakeUsers:
        def find_one(self, query):
            return {"_id": ObjectId(), "username": "alice", "password": "secret"}
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    res = user_service.get_user_by_username("alice")
    assert res["username"] == "alice"
    assert "password" not in res

def test_get_user_by_username_not_found(monkeypatch):
    class FakeUsers:
        def find_one(self, query):
            return None
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    with pytest.raises(NotFoundException):
        user_service.get_user_by_username("unknown")

# ----------------------
# UPDATE USER
# ----------------------
def test_update_user_success(monkeypatch):
    uid = ObjectId()
    updated_doc = {"_id": uid, "username": "alice", "name": "Bob", "allergen_preferences": []}

    class FakeUsers:
        def update_one(self, q, u):
            return None
        def find_one(self, q):
            return updated_doc

    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    uu = UserUpdate(name="Bob", allergen_preferences=[])
    res = user_service.update_user(str(uid), uu.model_dump(exclude_none=True))
    assert res["_id"] == str(uid)
    assert res["name"] == "Bob"
    assert "password" not in res

def test_update_user_empty_data():
    with pytest.raises(BadRequestException):
        user_service.update_user(str(ObjectId()), {})

def test_update_user_invalid_id():
    uu = UserUpdate(name="Bob", allergen_preferences=[])
    with pytest.raises(NotFoundException):
        user_service.update_user("invalid_id", uu.model_dump(exclude_none=True))

# ----------------------
# DELETE USER
# ----------------------
def test_delete_user_success(monkeypatch):
    class R:
        deleted_count = 1
    class FakeUsers:
        def delete_one(self, q):
            return R()
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    res = user_service.delete_user(str(ObjectId()))
    assert res is None

def test_delete_user_not_found(monkeypatch):
    class R:
        deleted_count = 0
    class FakeUsers:
        def delete_one(self, q):
            return R()
    monkeypatch.setattr(user_service.db, "users", FakeUsers())
    with pytest.raises(NotFoundException):
        user_service.delete_user(str(ObjectId()))
