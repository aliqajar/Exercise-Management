import pytest
from app.models import User, Exercise, Rating
from sqlalchemy.orm import Session
from app import auth

def test_create_user(test_db: Session):
    hashed_password = auth.get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    assert user.username == "testuser"
    assert user.hashed_password == hashed_password

def test_create_exercise(test_db: Session):
    # Create user first
    hashed_password = auth.get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create exercise
    exercise = Exercise(
        name="Test Exercise",
        description="Test Description",
        difficulty_level=3,
        is_public=True,
        creator_id=user.id
    )
    test_db.add(exercise)
    test_db.commit()
    test_db.refresh(exercise)
    
    assert exercise.name == "Test Exercise"
    assert exercise.creator_id == user.id

def test_exercise_user_relationship(test_db: Session):
    # Create user
    hashed_password = auth.get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    test_db.add(user)
    test_db.commit()
    
    # Create exercise with relationship
    exercise = Exercise(
        name="Test Exercise",
        description="Test Description",
        difficulty_level=3,
        is_public=True,
        creator_id=user.id
    )
    test_db.add(exercise)
    test_db.commit()
    
    # Query fresh instances
    db_user = test_db.query(User).filter(User.id == user.id).first()
    db_exercise = test_db.query(Exercise).filter(Exercise.id == exercise.id).first()
    
    # Test relationship
    assert len(db_user.exercises) == 1
    assert db_user.exercises[0].id == exercise.id
    assert db_exercise.creator.id == user.id

def test_favorite_relationship(test_db: Session):
    # Create user and exercise
    hashed_password = auth.get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    exercise = Exercise(
        name="Test Exercise",
        description="Test Description",
        difficulty_level=3,
        is_public=True
    )
    test_db.add_all([user, exercise])
    test_db.commit()
    test_db.refresh(user)
    test_db.refresh(exercise)
    
    # Add to favorites
    user.favorite_exercises.append(exercise)
    test_db.commit()
    test_db.refresh(user)
    test_db.refresh(exercise)
    
    # Test relationship
    assert exercise in user.favorite_exercises
    assert user in exercise.favorited_by

def test_rating_relationship(test_db: Session):
    # Create user and exercise
    hashed_password = auth.get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    exercise = Exercise(
        name="Test Exercise",
        description="Test Description",
        difficulty_level=3,
        is_public=True
    )
    test_db.add_all([user, exercise])
    test_db.commit()
    
    # Create rating
    rating = Rating(
        value=4,
        user_id=user.id,
        exercise_id=exercise.id
    )
    test_db.add(rating)
    test_db.commit()
    
    # Query fresh instances
    db_user = test_db.query(User).filter(User.id == user.id).first()
    db_exercise = test_db.query(Exercise).filter(Exercise.id == exercise.id).first()
    db_rating = test_db.query(Rating).filter(Rating.id == rating.id).first()
    
    # Test relationships
    assert len(db_user.ratings) == 1
    assert db_user.ratings[0].id == rating.id
    assert len(db_exercise.ratings) == 1
    assert db_exercise.ratings[0].id == rating.id
    assert db_rating.user.id == user.id
    assert db_rating.exercise.id == exercise.id
    assert db_rating.value == 4 