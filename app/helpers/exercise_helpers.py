from sqlalchemy.orm import Session
from .. import models, cache, cache_helpers
from ..exceptions import not_found_error, forbidden_error, ErrorMessage
from typing import Optional

def get_exercise_or_404(db: Session, exercise_id: str) -> models.Exercise:
    """Get exercise by ID or raise 404 error"""
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if not exercise:
        raise not_found_error(ErrorMessage.EXERCISE_NOT_FOUND)
    return exercise

def check_exercise_access(exercise: models.Exercise, current_user: Optional[models.User]) -> None:
    """Check if user can access the exercise"""
    if not exercise.is_public and (not current_user or current_user.id != exercise.creator_id):
        raise forbidden_error(ErrorMessage.UNAUTHORIZED_ACCESS)

def check_exercise_modification(
    exercise: models.Exercise,
    current_user: models.User,
    is_delete: bool = False
) -> None:
    """Check if user can modify the exercise.
    For updates: Public exercises can be modified by any user, private only by creator.
    For deletes: Only the creator can delete their exercises."""
    if is_delete:
        if exercise.creator_id != current_user.id:
            raise forbidden_error(ErrorMessage.UNAUTHORIZED_DELETE)
    elif not exercise.is_public and exercise.creator_id != current_user.id:
        raise forbidden_error(ErrorMessage.UNAUTHORIZED_UPDATE)

def handle_exercise_interaction(
    exercise: models.Exercise,
    current_user: models.User,
    interaction_type: str,
    add: bool
) -> None:
    """Handle adding/removing exercise interactions (favorites/saves)"""
    if interaction_type == "favorites":
        collection = current_user.favorite_exercises
        count_type = "favorites"
    else:
        collection = current_user.saved_exercises
        count_type = "saves"

    if add and exercise not in collection:
        collection.append(exercise)
        cache.increment_count(count_type, str(exercise.id))
    elif not add and exercise in collection:
        collection.remove(exercise)
        cache.decrement_count(count_type, str(exercise.id))
    
    # Invalidate exercise cache
    cache.invalidate_exercise_cache(str(exercise.id))

def prepare_exercise_response(
    exercise: models.Exercise,
    current_user: Optional[models.User] = None
) -> models.Exercise:
    """Prepare exercise for response by updating counts and interaction status"""
    cache_helpers.update_exercise_interaction_status(exercise, current_user)
    return exercise 