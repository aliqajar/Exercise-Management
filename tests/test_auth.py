import pytest
import uuid
from datetime import timedelta
from fastapi.testclient import TestClient
from fastapi import HTTPException
from app.main import app
from app import auth, schemas, models

@pytest.fixture(autouse=True)
def cleanup_db(test_db):
    """Cleanup the database after each test"""
    try:
        yield test_db
    finally:
        # Delete all users
        test_db.query(models.User).delete()
        test_db.commit()

@pytest.fixture
def db(test_db):
    """Get a test database session"""
    try:
        yield test_db
    finally:
        pass  # cleanup is handled by cleanup_db fixture

def test_get_current_user_no_token(db):
    """Test get_current_user with no token"""
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(db, None)
    assert exc_info.value.status_code == 401
    assert "not authenticated" in exc_info.value.detail.lower()

def test_get_optional_current_user_no_token(db):
    """Test get_optional_current_user with no token"""
    result = auth.get_optional_current_user(db, None)
    assert result is None

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = auth.get_password_hash(password)
    
    # Test that hashes are different for same password
    assert hashed != auth.get_password_hash(password)
    
    # Test verification
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrongpassword", hashed)

def test_token_creation_and_verification(db):
    """Test JWT token creation and verification"""
    # Create a test user with unique username
    username = f"tokentest_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    user = schemas.UserCreate(username=username, password=password)
    db_user = auth.create_user(db, user)
    
    # Create access token
    access_token = auth.create_access_token(data={"sub": username})
    assert access_token
    
    # Create refresh token
    refresh_token = auth.create_refresh_token(data={"sub": username})
    assert refresh_token
    
    # Verify tokens
    decoded_access = auth.verify_token(access_token)
    assert decoded_access["sub"] == username
    
    decoded_refresh = auth.verify_token(refresh_token, refresh_token=True)
    assert decoded_refresh["sub"] == username

def test_token_expiration(db):
    """Test token expiration"""
    username = f"expiretest_{uuid.uuid4().hex[:8]}"
    # Create token that's already expired
    access_token = auth.create_access_token(
        data={"sub": username},
        expires_delta=timedelta(seconds=-1)  # Token expired 1 second ago
    )
    
    # Verify token is expired
    with pytest.raises(HTTPException) as exc_info:
        auth.verify_token(access_token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()

def test_refresh_token_with_custom_expiry(db):
    """Test refresh token creation with custom expiry"""
    username = f"refreshtest_{uuid.uuid4().hex[:8]}"
    # Create refresh token with custom expiry
    refresh_token = auth.create_refresh_token(
        data={"sub": username},
        expires_delta=timedelta(days=30)
    )
    decoded = auth.verify_token(refresh_token, refresh_token=True)
    assert decoded["sub"] == username

def test_invalid_refresh_token(db):
    """Test invalid refresh token verification"""
    username = f"invalidrefresh_{uuid.uuid4().hex[:8]}"
    # Create access token (not a refresh token)
    access_token = auth.create_access_token(data={"sub": username})
    
    # Try to verify it as a refresh token
    with pytest.raises(HTTPException) as exc_info:
        auth.verify_token(access_token, refresh_token=True)
    assert exc_info.value.status_code == 401
    assert "invalid refresh token" in exc_info.value.detail.lower()

def test_invalid_token_format():
    """Test token with invalid format"""
    with pytest.raises(HTTPException) as exc_info:
        auth.verify_token("invalid_token_format")
    assert exc_info.value.status_code == 401
    assert "could not validate credentials" in exc_info.value.detail.lower()

def test_get_current_user_missing_username(db):
    """Test get_current_user with token missing username"""
    # Create token without 'sub' claim
    token = auth.create_access_token(data={"random": "data"})
    
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(db, token)
    assert exc_info.value.status_code == 401
    assert "could not validate credentials" in exc_info.value.detail.lower()

def test_get_current_user_nonexistent_user(db):
    """Test get_current_user with non-existent username"""
    # Create token with non-existent username
    token = auth.create_access_token(data={"sub": "nonexistent_user"})
    
    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(db, token)
    assert exc_info.value.status_code == 401
    assert "user not found" in exc_info.value.detail.lower()

def test_get_optional_current_user_invalid_token(db):
    """Test get_optional_current_user with invalid token"""
    result = auth.get_optional_current_user(db, "invalid_token")
    assert result is None

def test_get_current_user(db):
    """Test getting current user from token"""
    # Create a test user with unique username
    username = f"currentuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    user = schemas.UserCreate(username=username, password=password)
    db_user = auth.create_user(db, user)
    
    # Create token
    access_token = auth.create_access_token(data={"sub": username})
    
    # Get current user
    current_user = auth.get_current_user(db, access_token)
    assert current_user.username == username

def test_get_optional_current_user(db):
    """Test optional user authentication"""
    # Test with invalid token
    user = auth.get_optional_current_user(db, "invalid_token")
    assert user is None
    
    # Test with valid token
    username = f"optionaluser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    user = schemas.UserCreate(username=username, password=password)
    db_user = auth.create_user(db, user)
    access_token = auth.create_access_token(data={"sub": username})
    current_user = auth.get_optional_current_user(db, access_token)
    assert current_user.username == username

def test_auth_router_register(client):
    """Test user registration endpoint"""
    # Test successful registration
    username = f"newuser_{uuid.uuid4().hex[:8]}"
    response = client.post("/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == username
    
    # Test duplicate username
    response = client.post("/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    assert response.status_code == 400

def test_auth_router_token(client):
    """Test token endpoints"""
    username = f"tokenuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"
    
    # Register user
    client.post("/auth/register", json={
        "username": username,
        "password": password
    })
    
    # Test successful login
    response = client.post("/auth/token", 
        data={"username": username, "password": password})
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # Test invalid credentials
    response = client.post("/auth/token", 
        data={"username": username, "password": "wrongpass"})
    assert response.status_code == 401
    
    # Test refresh token
    response = client.post("/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    
    # Test invalid refresh token
    response = client.post("/auth/refresh", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == 401 