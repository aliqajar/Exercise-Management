from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth, cache_helpers
from ..database import get_db
from ..utils import InteractionType, validate_interaction_type
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/exercises", response_model=List[schemas.Exercise])
def get_user_exercises(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    exercises = db.query(models.Exercise).filter(models.Exercise.creator_id == str(user_id)).all()
    
    # Add interaction counts and status
    for exercise in exercises:
        cache_helpers.update_exercise_interaction_status(exercise, current_user)
    
    return exercises

@router.get("/{user_id}/interactions", response_model=List[schemas.Exercise])
def get_user_interactions(
    user_id: UUID,
    interaction_type: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    validated_type = validate_interaction_type(interaction_type)
    if not validated_type:
        raise HTTPException(status_code=422, detail="Invalid interaction type. Must be 'favorites' or 'saves'")
    
    exercises = user.favorite_exercises if validated_type == InteractionType.FAVORITE else user.saved_exercises
    
    # Add interaction counts and status
    for exercise in exercises:
        cache_helpers.update_exercise_interaction_status(exercise, current_user)
    
    return exercises 