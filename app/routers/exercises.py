from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth, cache
from ..database import get_db
from ..utils import InteractionType, validate_interaction_type
from ..exceptions import validation_error, ErrorMessage
from ..helpers.exercise_helpers import (
    get_exercise_or_404,
    check_exercise_access,
    check_exercise_modification,
    handle_exercise_interaction,
    prepare_exercise_response
)
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[schemas.Exercise])
def read_exercises(
    skip: int = 0,
    limit: int = 100,
    sort_by_difficulty: bool = False,
    name: Optional[str] = None,
    description: Optional[str] = None,
    difficulty_level: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get a list of exercises with optional filtering and sorting"""
    # Base query for public exercises
    query = db.query(models.Exercise).filter(models.Exercise.is_public == True)
    
    # If user is authenticated, also include their private exercises
    if current_user:
        query = db.query(models.Exercise).filter(
            (models.Exercise.is_public == True) | 
            (models.Exercise.creator_id == current_user.id)
        )
    
    # Apply filters
    if name:
        query = query.filter(models.Exercise.name.ilike(f"%{name}%"))
    if description:
        query = query.filter(models.Exercise.description.ilike(f"%{description}%"))
    if difficulty_level:
        query = query.filter(models.Exercise.difficulty_level == difficulty_level)
    
    # Apply sorting
    if sort_by_difficulty:
        query = query.order_by(models.Exercise.difficulty_level)
    
    exercises = query.offset(skip).limit(limit).all()
    return [prepare_exercise_response(exercise, current_user) for exercise in exercises]

@router.post("/", response_model=schemas.Exercise)
def create_exercise(
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_exercise = models.Exercise(**exercise.model_dump(), creator_id=current_user.id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/personal", response_model=List[schemas.Exercise])
def get_personal_exercises(
    type: Optional[str] = None,  # "favorites" or "saved" or None for both
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if type == "favorites":
        exercises = current_user.favorite_exercises
    elif type == "saved":
        exercises = current_user.saved_exercises
    else:
        # Combine and remove duplicates
        exercises = list(set(current_user.favorite_exercises + current_user.saved_exercises))
    
    # Add counts and personal status
    for exercise in exercises:
        # Try to get counts from cache first
        favorite_count = cache.get_cached_count("favorites", str(exercise.id))
        save_count = cache.get_cached_count("saves", str(exercise.id))
        
        if favorite_count is None:
            favorite_count = len(exercise.favorited_by)
            cache.cache_count("favorites", str(exercise.id), favorite_count)
        
        if save_count is None:
            save_count = len(exercise.saved_by)
            cache.cache_count("saves", str(exercise.id), save_count)
        
        exercise.favorite_count = favorite_count
        exercise.save_count = save_count
        exercise.is_favorited = exercise in current_user.favorite_exercises
        exercise.is_saved = exercise in current_user.saved_exercises
    
    return exercises

@router.get("/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get a specific exercise by ID"""
    exercise = get_exercise_or_404(db, exercise_id)
    check_exercise_access(exercise, current_user)
    return prepare_exercise_response(exercise, current_user)

@router.put("/{exercise_id}", response_model=schemas.Exercise)
async def update_exercise(
    exercise_id: str,
    exercise_update: schemas.ExerciseUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Update an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    check_exercise_modification(exercise, current_user)
    
    # Apply updates
    update_data = exercise_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    db.commit()
    cache.invalidate_exercise_cache(str(exercise_id))
    return prepare_exercise_response(exercise, current_user)

@router.delete("/{exercise_id}", status_code=status.HTTP_200_OK)
def delete_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Delete an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    check_exercise_modification(exercise, current_user, is_delete=True)
    
    db.delete(exercise)
    db.commit()
    
    # Invalidate caches
    cache.invalidate_exercise_cache(str(exercise.id))
    cache.cache_delete(cache.generate_key(f"{cache.COUNT_PREFIX}favorites:", str(exercise.id)))
    cache.cache_delete(cache.generate_key(f"{cache.COUNT_PREFIX}saves:", str(exercise.id)))
    
    return {"message": "Exercise deleted"}

@router.post("/{exercise_id}/favorite", response_model=schemas.Exercise)
def favorite_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Favorite an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    handle_exercise_interaction(exercise, current_user, "favorites", True)
    db.commit()
    return prepare_exercise_response(exercise, current_user)

@router.delete("/{exercise_id}/favorite", response_model=schemas.Exercise)
def unfavorite_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Remove favorite from an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    handle_exercise_interaction(exercise, current_user, "favorites", False)
    db.commit()
    return prepare_exercise_response(exercise, current_user)

@router.post("/{exercise_id}/save", response_model=schemas.Exercise)
def save_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Save an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    handle_exercise_interaction(exercise, current_user, "saves", True)
    db.commit()
    return prepare_exercise_response(exercise, current_user)

@router.delete("/{exercise_id}/save", response_model=schemas.Exercise)
def unsave_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Remove save from an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    handle_exercise_interaction(exercise, current_user, "saves", False)
    db.commit()
    return prepare_exercise_response(exercise, current_user)

@router.get("/{exercise_id}/interactions", response_model=List[schemas.User])
def get_exercise_interactions(
    exercise_id: str,
    interaction_type: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get users who have interacted with an exercise"""
    exercise = get_exercise_or_404(db, exercise_id)
    validated_type = validate_interaction_type(interaction_type)
    if not validated_type:
        raise validation_error(ErrorMessage.INVALID_INTERACTION_TYPE)
    
    return exercise.favorited_by if validated_type == InteractionType.FAVORITE else exercise.saved_by

@router.post("/{exercise_id}/rate", response_model=schemas.Rating)
def rate_exercise(
    exercise_id: UUID,
    rating: schemas.RatingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    exercise = db.query(models.Exercise).filter(models.Exercise.id == str(exercise_id)).first()
    if not exercise:
        raise validation_error(ErrorMessage.EXERCISE_NOT_FOUND)

    existing_rating = db.query(models.Rating).filter(
        models.Rating.exercise_id == str(exercise_id),
        models.Rating.user_id == current_user.id
    ).first()

    if existing_rating:
        existing_rating.value = rating.value
        existing_rating.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_rating)
        return existing_rating

    new_rating = models.Rating(
        value=rating.value,
        exercise_id=str(exercise_id),
        user_id=current_user.id
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@router.get("/{exercise_id}/ratings", response_model=List[schemas.Rating])
def get_exercise_ratings(
    exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    exercise = db.query(models.Exercise).filter(models.Exercise.id == str(exercise_id)).first()
    if not exercise:
        raise validation_error(ErrorMessage.EXERCISE_NOT_FOUND)

    ratings = db.query(models.Rating).filter(models.Rating.exercise_id == str(exercise_id)).all()
    return ratings 