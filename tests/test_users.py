import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session
from uuid import UUID

@pytest.fixture
def db():
    """Get a test database session"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def is_valid_uuid(uuid_str):
    """Check if a string is a valid UUID"""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def test_get_users(client):
    """Test getting list of users"""
    # Create some test users first
    usernames = ["testuser1", "testuser2", "testuser3"]
    for username in usernames:
        client.post("/auth/register", json={
            "username": username,
            "password": "testpass123"
        })
    
    # Test getting all users
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= len(usernames)
    assert all(user["username"] in usernames for user in users[:len(usernames)])

def test_get_user_by_id(client):
    """Test getting a specific user by ID"""
    # Create a test user
    response = client.post("/auth/register", json={
        "username": "userbyid",
        "password": "testpass123"
    })
    user_id = response.json()["id"]
    
    # Test getting the user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert user["username"] == "userbyid"
    
    # Test getting non-existent user with valid UUID
    non_existent_id = "00000000-0000-4000-a000-000000000000"
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404
    
    # Test getting user with invalid UUID
    response = client.get("/users/invalid-uuid")
    assert response.status_code == 422

def test_get_user_exercises(client):
    """Test getting a user's exercises"""
    # Create a test user and authenticate
    auth_response = client.post("/auth/register", json={
        "username": "exerciseuser",
        "password": "testpass123"
    })
    user_id = auth_response.json()["id"]
    
    # Login to get token
    token_response = client.post("/auth/token", 
        data={"username": "exerciseuser", "password": "testpass123"})
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create some exercises
    exercises = [
        {"name": "Exercise 1", "description": "Test 1", "difficulty_level": 1, "is_public": True},
        {"name": "Exercise 2", "description": "Test 2", "difficulty_level": 2, "is_public": False}
    ]
    created_exercises = []
    for exercise in exercises:
        response = client.post("/exercises/", json=exercise, headers=headers)
        assert response.status_code == 200
        created_exercises.append(response.json())
    
    # Test getting user's exercises
    response = client.get(f"/users/{user_id}/exercises", headers=headers)
    assert response.status_code == 200
    user_exercises = response.json()
    assert len(user_exercises) == len(exercises)
    assert all(ex["name"] in [e["name"] for e in exercises] for ex in user_exercises)

def test_get_user_interactions(client):
    """Test getting a user's exercise interactions"""
    # Create a test user and authenticate
    auth_response = client.post("/auth/register", json={
        "username": "interactionuser",
        "password": "testpass123"
    })
    user_id = auth_response.json()["id"]
    
    # Login to get token
    token_response = client.post("/auth/token", 
        data={"username": "interactionuser", "password": "testpass123"})
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an exercise and interact with it
    exercise_response = client.post("/exercises/", json={
        "name": "Test Exercise",
        "description": "For interaction test",
        "difficulty_level": 1,
        "is_public": True
    }, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # Favorite and save the exercise
    client.post(f"/exercises/{exercise_id}/favorite", headers=headers)
    client.post(f"/exercises/{exercise_id}/save", headers=headers)
    
    # Test getting user's favorites
    response = client.get(f"/users/{user_id}/interactions", params={"interaction_type": "favorites"}, headers=headers)
    assert response.status_code == 200
    favorites = response.json()
    assert len(favorites) == 1
    assert favorites[0]["id"] == exercise_id
    
    # Test getting user's saves
    response = client.get(f"/users/{user_id}/interactions", params={"interaction_type": "saves"}, headers=headers)
    assert response.status_code == 200
    saves = response.json()
    assert len(saves) == 1
    assert saves[0]["id"] == exercise_id
    
    # Test invalid interaction type
    response = client.get(f"/users/{user_id}/interactions", params={"interaction_type": "invalid"}, headers=headers)
    assert response.status_code == 422
    assert "Invalid interaction type" in response.json()["detail"] 