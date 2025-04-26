import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import auth

def create_test_user(client, username="testuser"):
    """Helper function to create and authenticate a test user"""
    # Register user
    user_data = {
        "username": username,
        "password": "testpassword"
    }
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 200
    
    # Login to get tokens
    login_response = client.post("/auth/token", 
        data={"username": username, "password": "testpassword"})
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    return {
        "user": register_response.json(),
        "tokens": tokens
    }

def get_auth_headers(tokens):
    """Helper function to create authorization headers"""
    return {"Authorization": f"Bearer {tokens['access_token']}"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_create_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    exercise_data = {
        "name": "Push-ups",
        "description": "Basic upper body exercise",
        "difficulty_level": 2,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exercise_data["name"]
    assert data["description"] == exercise_data["description"]
    assert data["difficulty_level"] == exercise_data["difficulty_level"]
    assert "id" in data
    assert data["creator_id"] == auth_data["user"]["id"]

def test_get_exercises(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    # First create an exercise
    exercise_data = {
        "name": "Squats",
        "description": "Basic lower body exercise",
        "difficulty_level": 3,
        "is_public": True
    }
    client.post("/exercises/", json=exercise_data, headers=headers)
    
    # Get list of exercises (no auth required for public exercises)
    response = client.get("/exercises/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(exercise["name"] == "Squats" for exercise in data)

def test_create_user(client):
    user_data = {
        "username": "newuser",
        "password": "testpassword"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data

def test_get_users(client):
    # First create a user
    user_data = {
        "username": "testuser2",
        "password": "testpassword"
    }
    client.post("/auth/register", json=user_data)
    
    # Get list of users
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(user["username"] == "testuser2" for user in data)

def test_get_exercise_by_id(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    # First create an exercise
    exercise_data = {
        "name": "Lunges",
        "description": "Lower body exercise",
        "difficulty_level": 2,
        "is_public": True
    }
    create_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = create_response.json()["id"]
    
    # Get the exercise by ID (no auth required for public exercises)
    response = client.get(f"/exercises/{exercise_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exercise_data["name"]
    assert data["id"] == exercise_id

def test_update_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    # First create an exercise
    exercise_data = {
        "name": "Old Exercise",
        "description": "Old description",
        "difficulty_level": 1,
        "is_public": True
    }
    create_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = create_response.json()["id"]
    
    # Update the exercise
    update_data = {
        "name": "Updated Exercise",
        "description": "Updated description",
        "difficulty_level": 3
    }
    response = client.put(f"/exercises/{exercise_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["difficulty_level"] == update_data["difficulty_level"]

def test_delete_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    # First create an exercise
    exercise_data = {
        "name": "Exercise to Delete",
        "description": "This will be deleted",
        "difficulty_level": 1,
        "is_public": True
    }
    create_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = create_response.json()["id"]
    
    # Delete the exercise
    response = client.delete(f"/exercises/{exercise_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/exercises/{exercise_id}")
    assert get_response.status_code == 404

def test_favorite_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser3")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise to Favorite",
        "description": "This will be favorited",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # Favorite the exercise
    response = client.post(f"/exercises/{exercise_id}/favorite", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorited"] is True
    assert data["favorite_count"] == 1

def test_unfavorite_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser4")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise to Unfavorite",
        "description": "This will be unfavorited",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # First favorite the exercise
    client.post(f"/exercises/{exercise_id}/favorite", headers=headers)
    
    # Then unfavorite it
    response = client.delete(f"/exercises/{exercise_id}/favorite", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorited"] is False
    assert data["favorite_count"] == 0

def test_save_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser5")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise to Save",
        "description": "This will be saved",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # Save the exercise
    response = client.post(f"/exercises/{exercise_id}/save", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_saved"] is True
    assert data["save_count"] == 1

def test_unsave_exercise(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser6")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise to Unsave",
        "description": "This will be unsaved",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # First save the exercise
    client.post(f"/exercises/{exercise_id}/save", headers=headers)
    
    # Then unsave it
    response = client.delete(f"/exercises/{exercise_id}/save", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_saved"] is False
    assert data["save_count"] == 0

def test_get_personal_exercises(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser7")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create two exercises
    exercise1_data = {
        "name": "Exercise for Personal List 1",
        "description": "This will be favorited",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise2_data = {
        "name": "Exercise for Personal List 2",
        "description": "This will be saved",
        "difficulty_level": 2,
        "is_public": True
    }
    exercise1_response = client.post("/exercises/", json=exercise1_data, headers=headers)
    exercise2_response = client.post("/exercises/", json=exercise2_data, headers=headers)
    exercise1_id = exercise1_response.json()["id"]
    exercise2_id = exercise2_response.json()["id"]
    
    # Favorite exercise1 and save exercise2
    client.post(f"/exercises/{exercise1_id}/favorite", headers=headers)
    client.post(f"/exercises/{exercise2_id}/save", headers=headers)
    
    # Get personal list
    response = client.get("/exercises/personal", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(ex["name"] == "Exercise for Personal List 1" and ex["is_favorited"] for ex in data)
    assert any(ex["name"] == "Exercise for Personal List 2" and ex["is_saved"] for ex in data)
    
    # Test filtering by favorites
    response = client.get("/exercises/personal?type=favorites", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Exercise for Personal List 1"
    
    # Test filtering by saves
    response = client.get("/exercises/personal?type=saved", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Exercise for Personal List 2"

def test_get_exercise_interactions(client):
    # Create two users
    auth_data1 = create_test_user(client, "testuser8")
    auth_data2 = create_test_user(client, "testuser9")
    headers1 = get_auth_headers(auth_data1["tokens"])
    headers2 = get_auth_headers(auth_data2["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise for Interactions",
        "description": "This will have interactions",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers1)
    exercise_id = exercise_response.json()["id"]
    
    # Have both users favorite and save the exercise
    client.post(f"/exercises/{exercise_id}/favorite", headers=headers1)
    client.post(f"/exercises/{exercise_id}/favorite", headers=headers2)
    client.post(f"/exercises/{exercise_id}/save", headers=headers1)
    
    # Get users who favorited
    response = client.get(f"/exercises/{exercise_id}/interactions?interaction_type=favorites", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = [user["username"] for user in data]
    assert "testuser8" in usernames
    assert "testuser9" in usernames
    
    # Get users who saved
    response = client.get(f"/exercises/{exercise_id}/interactions?interaction_type=saves", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "testuser8"

def test_exercise_counts_in_list(client):
    # Create and authenticate user
    auth_data = create_test_user(client, "testuser10")
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise with Counts",
        "description": "This will have counts",
        "difficulty_level": 1,
        "is_public": True
    }
    exercise_response = client.post("/exercises/", json=exercise_data, headers=headers)
    exercise_id = exercise_response.json()["id"]
    
    # Favorite and save the exercise
    client.post(f"/exercises/{exercise_id}/favorite", headers=headers)
    client.post(f"/exercises/{exercise_id}/save", headers=headers)
    
    # Get exercise list
    response = client.get("/exercises/")
    assert response.status_code == 200
    data = response.json()
    exercise = next(ex for ex in data if ex["id"] == exercise_id)
    assert exercise["favorite_count"] == 1
    assert exercise["save_count"] == 1

def test_exercise_cache(client):
    # Create and authenticate user
    auth_data = create_test_user(client)
    headers = get_auth_headers(auth_data["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise for Cache Test",
        "description": "Testing cache functionality",
        "difficulty_level": 3,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise_data, headers=headers)
    assert response.status_code == 200
    exercise_id = response.json()["id"]
    
    # First request should cache the exercise
    response1 = client.get(f"/exercises/{exercise_id}")
    assert response1.status_code == 200
    
    # Second request should use cached data
    response2 = client.get(f"/exercises/{exercise_id}")
    assert response2.status_code == 200
    assert response2.json() == response1.json()
    
    # Update exercise should invalidate cache
    update_data = {"name": "Updated Exercise Name"}
    response = client.put(f"/exercises/{exercise_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    
    # Next request should get fresh data
    response3 = client.get(f"/exercises/{exercise_id}")
    assert response3.status_code == 200
    assert response3.json()["name"] == "Updated Exercise Name"
    assert response3.json() != response2.json()

def test_favorite_count_cache(client):
    # Create and authenticate two users
    auth_data1 = create_test_user(client, "cacheuser1")
    auth_data2 = create_test_user(client, "cacheuser2")
    headers1 = get_auth_headers(auth_data1["tokens"])
    headers2 = get_auth_headers(auth_data2["tokens"])
    
    # Create an exercise
    exercise_data = {
        "name": "Exercise for Cache Count Test",
        "description": "Testing cache count functionality",
        "difficulty_level": 3,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise_data, headers=headers1)
    assert response.status_code == 200
    exercise_id = response.json()["id"]
    
    # Initial favorite count should be 0
    response = client.get(f"/exercises/{exercise_id}")
    assert response.status_code == 200
    assert response.json()["favorite_count"] == 0
    
    # First user favorites
    response = client.post(f"/exercises/{exercise_id}/favorite", headers=headers1)
    assert response.status_code == 200
    assert response.json()["favorite_count"] == 1
    
    # Second user favorites
    response = client.post(f"/exercises/{exercise_id}/favorite", headers=headers2)
    assert response.status_code == 200
    assert response.json()["favorite_count"] == 2
    
    # Verify count in list endpoint
    response = client.get("/exercises/")
    assert response.status_code == 200
    exercise = next(ex for ex in response.json() if ex["id"] == exercise_id)
    assert exercise["favorite_count"] == 2
    
    # First user unfavorites
    response = client.delete(f"/exercises/{exercise_id}/favorite", headers=headers1)
    assert response.status_code == 200
    assert response.json()["favorite_count"] == 1

def test_health_check_redis(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "redis_status" in data
    assert data["redis_status"]["status"] == "healthy"
    assert "message" in data["redis_status"]
    assert "timestamp" in data["redis_status"] 