import pytest
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base, get_db, engine, SessionLocal
from app.models import User, Exercise
import uuid

@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up database after each test"""
    yield
    db = next(get_db())
    try:
        db.execute(text("DELETE FROM users"))
        db.execute(text("DELETE FROM exercises"))
        db.commit()
    finally:
        db.close()

def test_database_connection():
    """Test database connection and session creation"""
    try:
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
        
        # Test session creation
        session = SessionLocal()
        try:
            assert isinstance(session, Session)
        finally:
            session.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")

def test_get_db():
    """Test the get_db dependency"""
    db = next(get_db())
    try:
        # Test that we can execute queries
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        # Test that we can create and query models
        test_id = str(uuid.uuid4())
        user = User(id=test_id, username=f"dbtest_{test_id}", hashed_password="test")
        db.add(user)
        db.commit()
        
        queried_user = db.query(User).filter(User.id == test_id).first()
        assert queried_user is not None
        assert queried_user.username == f"dbtest_{test_id}"
    finally:
        # Clean up
        db.rollback()
        db.close()

def test_database_migrations():
    """Test that all tables are created properly"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get list of all tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check that all model tables exist
    assert "users" in tables
    assert "exercises" in tables
    assert "favorites" in tables
    assert "saves" in tables
    assert "ratings" in tables
    
    # Check table columns
    user_columns = {col["name"] for col in inspector.get_columns("users")}
    assert "id" in user_columns
    assert "username" in user_columns
    assert "hashed_password" in user_columns
    assert "created_at" in user_columns
    assert "updated_at" in user_columns
    
    exercise_columns = {col["name"] for col in inspector.get_columns("exercises")}
    assert "id" in exercise_columns
    assert "name" in exercise_columns
    assert "description" in exercise_columns
    assert "difficulty_level" in exercise_columns
    assert "is_public" in exercise_columns
    assert "creator_id" in exercise_columns

def test_session_rollback():
    """Test session rollback functionality"""
    db = next(get_db())
    try:
        # Create first user with unique ID and username
        test_id1 = str(uuid.uuid4())
        user1 = User(id=test_id1, username=f"rollbacktest_{test_id1}", hashed_password="test1")
        db.add(user1)
        db.commit()
        
        # Try to create a user with same username
        test_id2 = str(uuid.uuid4())
        user2 = User(id=test_id2, username=f"rollbacktest_{test_id1}", hashed_password="test2")
        db.add(user2)
        with pytest.raises(Exception):
            db.commit()
        
        db.rollback()  # Explicitly rollback after exception
        
        # Verify the second user was not created
        users = db.query(User).filter(User.username == f"rollbacktest_{test_id1}").all()
        assert len(users) == 1
        assert users[0].hashed_password == "test1"
    finally:
        db.rollback()
        db.close()

def test_cascade_delete():
    """Test cascade delete functionality"""
    db = next(get_db())
    try:
        # Create a user and associated exercise with unique IDs
        test_user_id = str(uuid.uuid4())
        user = User(id=test_user_id, username=f"cascadetest_{test_user_id}", hashed_password="test")
        db.add(user)
        db.commit()
        
        test_exercise_id = str(uuid.uuid4())
        exercise = Exercise(
            id=test_exercise_id,
            name="Test Exercise",
            description="Test",
            difficulty_level=1,
            is_public=True,
            creator_id=user.id
        )
        db.add(exercise)
        db.commit()
        
        # Delete the user and verify cascade
        db.delete(user)
        db.commit()
        
        # Verify exercise was also deleted
        deleted_exercise = db.query(Exercise).filter(Exercise.id == test_exercise_id).first()
        assert deleted_exercise is None
    finally:
        db.rollback()
        db.close() 