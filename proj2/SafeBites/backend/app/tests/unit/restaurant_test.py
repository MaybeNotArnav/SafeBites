import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_restaurant():
    return {
        "name": "Testaurant",
        "location": "123 Test St",
        "cuisine": ["Test Cuisine"],
        "rating": 4.5
    }

@patch("app.services.restaurant_service.restaurant_collection")
def test_create_restaurant(mock_collection, sample_restaurant):
    mock_result = MagicMock()
    mock_result.inserted_id = "abc12345" 
    mock_collection.insert_one.return_value = mock_result
    response = client.post("/restaurants/",json=sample_restaurant)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["id"] == "abc12345"

@patch("app.services.restaurant_service.restaurant_collection")
def test_list_restaurants(mock_collection):
    mock_collection.find.return_value = [
        {"_id": "abc12345", "name": "Testaurant", "location": "123 Test St", "cuisine": ["Test Cuisine"], "rating": 4.5}
      , {"_id": "def67890", "name": "Food Place", "location": "456 Food Ave", "cuisine": ["Food Cuisine"], "rating": 4.0}
    ]

    response = client.get("/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)
    assert data[0]["name"] == "Testaurant"

@patch("app.services.restaurant_service.restaurant_collection")
def test_get_restaurant_by_id(mock_collection):
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Testaurant",
        "location": "123 Test St",
        "cuisine": ["Test Cuisine"],
        "rating": 4.5
    }

    response = client.get("/restaurants/507f1f77bcf86cd799439011")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Testaurant"

@patch("app.services.restaurant_service.restaurant_collection")
def test_update_restaurant(mock_collection):
    mock_collection.update_one.return_value = MagicMock(matched_count=1,modified_count=1)
    mock_collection.find_one.return_value = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Updated Testaurant",
        "location": "123 Test St",
        "cuisine": ["Test Cuisine"],
        "rating": 4.5
    }

    response = client.patch("/restaurants/507f1f77bcf86cd799439011", json={"name": "Updated Testaurant"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Testaurant"

@patch("app.services.restaurant_service.restaurant_collection")
def test_delete_restaurant(mock_collection):
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    response = client.delete("/restaurants/507f1f77bcf86cd799439011")
    assert response.status_code == 200
    data = response.json()
    assert "Restaurant with ID 507f1f77bcf86cd799439011 deleted successfully." in data["message"]
