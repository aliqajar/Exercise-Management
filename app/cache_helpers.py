from typing import Tuple
from . import cache, models

def get_interaction_counts(exercise: models.Exercise) -> Tuple[int, int]:
    """Get favorite and save counts for an exercise from cache or database"""
    # Try to get counts from cache first
    favorite_count = cache.get_cached_count("favorites", str(exercise.id))
    save_count = cache.get_cached_count("saves", str(exercise.id))
    
    if favorite_count is None:
        favorite_count = len(exercise.favorited_by)
        cache.cache_count("favorites", str(exercise.id), favorite_count)
    
    if save_count is None:
        save_count = len(exercise.saved_by)
        cache.cache_count("saves", str(exercise.id), save_count)
    
    return favorite_count, save_count

def update_exercise_interaction_status(exercise: models.Exercise, current_user: models.User = None) -> None:
    """Update exercise with interaction counts and user's interaction status"""
    favorite_count, save_count = get_interaction_counts(exercise)
    exercise.favorite_count = favorite_count
    exercise.save_count = save_count
    
    if current_user:
        exercise.is_favorited = exercise in current_user.favorite_exercises
        exercise.is_saved = exercise in current_user.saved_exercises 