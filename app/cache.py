import json
import os
from typing import Any, Optional, Union
from redis import Redis
from datetime import timedelta

# Redis client instance
redis_client = Redis.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True  # Automatically decode responses to strings
)

# Key prefixes for different types of data
EXERCISE_PREFIX = "exercise:"
USER_PREFIX = "user:"
COUNT_PREFIX = "count:"

def generate_key(prefix: str, id: str) -> str:
    """Generate a Redis key with the given prefix and ID"""
    return f"{prefix}{id}"

def cache_get(key: str) -> Optional[dict]:
    """Get a value from cache"""
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None

def cache_set(key: str, value: Any, expire: Optional[Union[int, timedelta]] = None) -> bool:
    """Set a value in cache with optional expiration"""
    try:
        redis_client.set(key, json.dumps(value), ex=expire)
        return True
    except Exception:
        return False

def cache_delete(key: str) -> bool:
    """Delete a value from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False

def cache_increment(key: str, amount: int = 1) -> Optional[int]:
    """Increment a counter in cache"""
    try:
        return redis_client.incrby(key, amount)
    except Exception:
        return None

def cache_decrement(key: str, amount: int = 1) -> Optional[int]:
    """Decrement a counter in cache"""
    try:
        return redis_client.decrby(key, amount)
    except Exception:
        return None

# Exercise-specific cache functions
def get_cached_exercise(exercise_id: str) -> Optional[dict]:
    """Get an exercise from cache"""
    return cache_get(generate_key(EXERCISE_PREFIX, exercise_id))

def cache_exercise(exercise_id: str, exercise_data: dict, expire: int = 3600) -> bool:
    """Cache an exercise for 1 hour by default"""
    return cache_set(generate_key(EXERCISE_PREFIX, exercise_id), exercise_data, expire)

def invalidate_exercise_cache(exercise_id: str) -> bool:
    """Invalidate exercise cache"""
    return cache_delete(generate_key(EXERCISE_PREFIX, exercise_id))

# Counter cache functions
def get_cached_count(count_type: str, id: str) -> Optional[int]:
    """Get a cached counter value"""
    try:
        value = redis_client.get(generate_key(f"{COUNT_PREFIX}{count_type}:", id))
        return int(value) if value else None
    except Exception:
        return None

def cache_count(count_type: str, id: str, value: int) -> bool:
    """Cache a counter value"""
    return cache_set(generate_key(f"{COUNT_PREFIX}{count_type}:", id), value)

def increment_count(count_type: str, id: str) -> Optional[int]:
    """Increment a cached counter"""
    return cache_increment(generate_key(f"{COUNT_PREFIX}{count_type}:", id))

def decrement_count(count_type: str, id: str) -> Optional[int]:
    """Decrement a cached counter"""
    return cache_decrement(generate_key(f"{COUNT_PREFIX}{count_type}:", id))

# Health check function
def check_redis_connection() -> tuple[bool, str]:
    """Check if Redis connection is healthy.
    
    Returns:
        tuple: (is_healthy: bool, message: str)
    """
    try:
        redis_client.ping()
        return True, "Redis connection is healthy"
    except Exception as e:
        return False, f"Redis connection error: {str(e)}" 