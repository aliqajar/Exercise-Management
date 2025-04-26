import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models, auth
import uuid

@pytest.fixture(autouse=True)
def cleanup_db(test_db):
    """Cleanup the database after each test"""
    try:
        yield test_db
    finally:
        # Delete all data
        test_db.query(models.Exercise).delete()
        test_db.query(models.User).delete()
        test_db.commit()

@pytest.fixture
def db(test_db):
    """Get a test database session"""
    try:
        yield test_db
    finally:
        pass  # cleanup is handled by cleanup_db fixture

@pytest.fixture
def test_user(db):
    """Create a test user"""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    user = models.User(
        username=username,
        hashed_password=auth.get_password_hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": user, "password": password}

@pytest.fixture
def test_user2(db):
    """Create another test user"""
    username = f"testuser2_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    user = models.User(
        username=username,
        hashed_password=auth.get_password_hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": user, "password": password}

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    response = client.post("/auth/token",
        data={"username": test_user["user"].username, "password": test_user["password"]})
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

@pytest.fixture
def auth_headers2(test_user2):
    """Get authentication headers for second test user"""
    response = client.post("/auth/token",
        data={"username": test_user2["user"].username, "password": test_user2["password"]})
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}

client = TestClient(app)

def test_create_exercise(auth_headers):
    """Test creating an exercise"""
    exercise_data = {
        "name": "Test Exercise",
        "description": "Test Description",
        "difficulty_level": 3,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exercise_data["name"]
    assert data["description"] == exercise_data["description"]
    assert data["difficulty_level"] == exercise_data["difficulty_level"]
    assert data["is_public"] == exercise_data["is_public"]
    assert "id" in data
    assert "creator_id" in data

def test_read_exercises(auth_headers, test_user):
    """Test reading exercises"""
    # Create some exercises
    exercises = [
        {"name": "Exercise 1", "description": "Public", "difficulty_level": 1, "is_public": True},
        {"name": "Exercise 2", "description": "Private", "difficulty_level": 2, "is_public": False}
    ]
    created = []
    for ex in exercises:
        response = client.post("/exercises/", json=ex, headers=auth_headers)
        created.append(response.json())
    
    # Test unauthenticated access (should only see public exercises)
    response = client.get("/exercises/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Exercise 1"
    
    # Test authenticated access (should see all exercises)
    response = client.get("/exercises/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {ex["name"] for ex in data} == {"Exercise 1", "Exercise 2"}

def test_read_exercise(auth_headers, auth_headers2):
    """Test reading a specific exercise"""
    # Create a public and private exercise
    exercises = [
        {"name": "Public Exercise", "description": "Public", "difficulty_level": 1, "is_public": True},
        {"name": "Private Exercise", "description": "Private", "difficulty_level": 2, "is_public": False}
    ]
    created = []
    for ex in exercises:
        response = client.post("/exercises/", json=ex, headers=auth_headers)
        created.append(response.json())
    
    # Test reading public exercise (unauthenticated)
    response = client.get(f"/exercises/{created[0]['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Public Exercise"
    
    # Test reading private exercise (unauthenticated)
    response = client.get(f"/exercises/{created[1]['id']}")
    assert response.status_code == 403
    
    # Test reading private exercise (different user)
    response = client.get(f"/exercises/{created[1]['id']}", headers=auth_headers2)
    assert response.status_code == 403
    
    # Test reading private exercise (owner)
    response = client.get(f"/exercises/{created[1]['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Private Exercise"
    
    # Test reading non-existent exercise
    response = client.get("/exercises/nonexistent-id")
    assert response.status_code == 404

def test_update_exercise(auth_headers, auth_headers2):
    """Test updating an exercise"""
    # Create an exercise
    exercise = {
        "name": "Original Exercise",
        "description": "Original Description",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Update exercise
    update_data = {
        "name": "Updated Exercise",
        "description": "Updated Description",
        "difficulty_level": 2
    }
    
    # Test updating with different user
    response = client.put(f"/exercises/{created['id']}", json=update_data, headers=auth_headers2)
    assert response.status_code == 200  # Public exercises can be modified by any user
    
    # Make exercise private
    response = client.put(f"/exercises/{created['id']}", 
        json={"is_public": False}, headers=auth_headers)
    assert response.status_code == 200
    
    # Try updating private exercise with different user
    response = client.put(f"/exercises/{created['id']}", json=update_data, headers=auth_headers2)
    assert response.status_code == 403
    
    # Update private exercise with owner
    response = client.put(f"/exercises/{created['id']}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]
    assert updated["description"] == update_data["description"]
    assert updated["difficulty_level"] == update_data["difficulty_level"]

def test_delete_exercise(auth_headers, auth_headers2):
    """Test deleting an exercise"""
    # Create an exercise
    exercise = {
        "name": "Exercise to Delete",
        "description": "Will be deleted",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Try deleting with different user
    response = client.delete(f"/exercises/{created['id']}", headers=auth_headers2)
    assert response.status_code == 403
    
    # Delete with owner
    response = client.delete(f"/exercises/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify exercise is deleted
    response = client.get(f"/exercises/{created['id']}")
    assert response.status_code == 404

def test_favorite_exercise(auth_headers):
    """Test favoriting and unfavoriting an exercise"""
    # Create an exercise
    exercise = {
        "name": "Exercise to Favorite",
        "description": "Test favoriting",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Favorite the exercise
    response = client.post(f"/exercises/{created['id']}/favorite", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorited"] == True
    
    # Unfavorite the exercise
    response = client.delete(f"/exercises/{created['id']}/favorite", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorited"] == False

def test_save_exercise(auth_headers):
    """Test saving and unsaving an exercise"""
    # Create an exercise
    exercise = {
        "name": "Exercise to Save",
        "description": "Test saving",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Save the exercise
    response = client.post(f"/exercises/{created['id']}/save", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_saved"] == True
    
    # Unsave the exercise
    response = client.delete(f"/exercises/{created['id']}/save", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_saved"] == False

def test_get_personal_exercises(auth_headers):
    """Test getting personal exercises"""
    # Create some exercises
    exercises = [
        {"name": "Exercise 1", "description": "Test 1", "difficulty_level": 1, "is_public": True},
        {"name": "Exercise 2", "description": "Test 2", "difficulty_level": 2, "is_public": True}
    ]
    created = []
    for ex in exercises:
        response = client.post("/exercises/", json=ex, headers=auth_headers)
        created.append(response.json())
    
    # Favorite first exercise and save second exercise
    client.post(f"/exercises/{created[0]['id']}/favorite", headers=auth_headers)
    client.post(f"/exercises/{created[1]['id']}/save", headers=auth_headers)
    
    # Test getting favorites
    response = client.get("/exercises/personal", params={"type": "favorites"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Exercise 1"
    
    # Test getting saved
    response = client.get("/exercises/personal", params={"type": "saved"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Exercise 2"
    
    # Test getting both
    response = client.get("/exercises/personal", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_exercise_interactions(auth_headers, auth_headers2):
    """Test getting exercise interactions"""
    # Create an exercise
    exercise = {
        "name": "Exercise for Interactions",
        "description": "Test interactions",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Have both users favorite and save the exercise
    client.post(f"/exercises/{created['id']}/favorite", headers=auth_headers)
    client.post(f"/exercises/{created['id']}/save", headers=auth_headers)
    client.post(f"/exercises/{created['id']}/favorite", headers=auth_headers2)
    client.post(f"/exercises/{created['id']}/save", headers=auth_headers2)
    
    # Test getting favorites
    response = client.get(f"/exercises/{created['id']}/interactions", 
        params={"interaction_type": "favorites"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Test getting saves
    response = client.get(f"/exercises/{created['id']}/interactions", 
        params={"interaction_type": "saves"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Test invalid interaction type
    response = client.get(f"/exercises/{created['id']}/interactions", 
        params={"interaction_type": "invalid"}, headers=auth_headers)
    assert response.status_code == 400

def test_cascade_delete(auth_headers, test_user, db):
    """Test that when a user is deleted, their exercises are also deleted"""
    # Create an exercise
    exercise = {
        "name": "Exercise to Cascade Delete",
        "description": "Should be deleted when user is deleted",
        "difficulty_level": 1,
        "is_public": True
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    created = response.json()
    
    # Delete the user
    db.delete(test_user["user"])
    db.commit()
    
    # Verify exercise was deleted
    response = client.get(f"/exercises/{created['id']}")
    assert response.status_code == 404

def test_sort_exercises_by_difficulty(client, test_db, test_user, auth_headers):
    # Create exercises with different difficulty levels
    exercises = [
        {"name": "Easy Exercise", "description": "Easy", "difficulty_level": 1, "is_public": True},
        {"name": "Hard Exercise", "description": "Hard", "difficulty_level": 5, "is_public": True},
        {"name": "Medium Exercise", "description": "Medium", "difficulty_level": 3, "is_public": True}
    ]
    
    for exercise in exercises:
        response = client.post(
            "/exercises/",
            json=exercise,
            headers=auth_headers
        )
        assert response.status_code == 200
    
    # Get sorted exercises
    response = client.get("/exercises/?sort_by_difficulty=true")
    assert response.status_code == 200
    
    sorted_exercises = response.json()
    difficulties = [ex["difficulty_level"] for ex in sorted_exercises]
    assert difficulties == sorted(difficulties)

def test_filter_exercises(client, test_db, test_user, auth_headers):
    # Create test exercises
    exercises = [
        {"name": "Push-up", "description": "Basic push-up", "difficulty_level": 2, "is_public": True},
        {"name": "Pull-up", "description": "Advanced pull-up", "difficulty_level": 4, "is_public": True},
        {"name": "Squat", "description": "Basic squat", "difficulty_level": 2, "is_public": True}
    ]
    
    for exercise in exercises:
        response = client.post(
            "/exercises/",
            json=exercise,
            headers=auth_headers
        )
        assert response.status_code == 200
    
    # Test name filter
    response = client.get("/exercises/?name=push")
    assert response.status_code == 200
    filtered_exercises = response.json()
    assert len(filtered_exercises) == 1
    assert filtered_exercises[0]["name"] == "Push-up"
    
    # Test description filter
    response = client.get("/exercises/?description=basic")
    assert response.status_code == 200
    filtered_exercises = response.json()
    assert len(filtered_exercises) == 2
    
    # Test difficulty level filter
    response = client.get("/exercises/?difficulty_level=2")
    assert response.status_code == 200
    filtered_exercises = response.json()
    assert len(filtered_exercises) == 2
    assert all(ex["difficulty_level"] == 2 for ex in filtered_exercises)

def test_rate_exercise(client, test_db, test_user, auth_headers):
    # Create an exercise
    exercise_data = {
        "name": "Test Exercise",
        "description": "Test Description",
        "difficulty_level": 3,
        "is_public": True
    }
    
    response = client.post(
        "/exercises/",
        json=exercise_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    exercise_id = response.json()["id"]
    
    # Rate the exercise
    rating_data = {"value": 4}
    response = client.post(
        f"/exercises/{exercise_id}/rate",
        json=rating_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Get exercise ratings
    response = client.get(
        f"/exercises/{exercise_id}/ratings",
        headers=auth_headers
    )
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) == 1
    assert ratings[0]["value"] == 4

def test_update_rating(client, test_db, test_user, auth_headers):
    # Create an exercise
    exercise_data = {
        "name": "Test Exercise",
        "description": "Test Description",
        "difficulty_level": 3,
        "is_public": True
    }
    
    response = client.post(
        "/exercises/",
        json=exercise_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    exercise_id = response.json()["id"]
    
    # Rate the exercise initially
    rating_data = {"value": 3}
    response = client.post(
        f"/exercises/{exercise_id}/rate",
        json=rating_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Update the rating
    updated_rating_data = {"value": 5}
    response = client.post(
        f"/exercises/{exercise_id}/rate",
        json=updated_rating_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify the updated rating
    response = client.get(
        f"/exercises/{exercise_id}/ratings",
        headers=auth_headers
    )
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) == 1
    assert ratings[0]["value"] == 5 