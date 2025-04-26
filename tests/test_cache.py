import pytest
from app import cache
from datetime import timedelta

@pytest.fixture(autouse=True)
def clear_redis():
    """Clear Redis before and after each test"""
    cache.redis_client.flushdb()
    yield
    cache.redis_client.flushdb()

def test_cache_set_get():
    # Test basic set/get
    test_data = {"name": "Test Exercise", "difficulty": 3}
    assert cache.cache_set("test:1", test_data)
    assert cache.cache_get("test:1") == test_data
    
    # Test with expiration
    assert cache.cache_set("test:2", test_data, expire=1)  # 1 second expiration
    assert cache.cache_get("test:2") == test_data
    
    # Test with timedelta expiration
    assert cache.cache_set("test:3", test_data, expire=timedelta(seconds=1))
    assert cache.cache_get("test:3") == test_data

def test_cache_delete():
    test_data = {"name": "Test Exercise"}
    cache.cache_set("test:delete", test_data)
    assert cache.cache_get("test:delete") == test_data
    
    assert cache.cache_delete("test:delete")
    assert cache.cache_get("test:delete") is None

def test_cache_increment_decrement():
    # Test increment
    assert cache.cache_increment("test:counter") == 1
    assert cache.cache_increment("test:counter") == 2
    assert cache.cache_increment("test:counter", 3) == 5
    
    # Test decrement
    assert cache.cache_decrement("test:counter") == 4
    assert cache.cache_decrement("test:counter", 2) == 2

def test_exercise_cache():
    exercise_data = {
        "id": "123",
        "name": "Test Exercise",
        "description": "Test Description",
        "difficulty_level": 3,
        "is_public": True
    }
    
    # Test caching exercise
    assert cache.cache_exercise("123", exercise_data)
    assert cache.get_cached_exercise("123") == exercise_data
    
    # Test invalidating exercise cache
    assert cache.invalidate_exercise_cache("123")
    assert cache.get_cached_exercise("123") is None

def test_counter_cache():
    # Test setting counter
    assert cache.cache_count("favorites", "123", 5)
    assert cache.get_cached_count("favorites", "123") == 5
    
    # Test incrementing counter
    assert cache.increment_count("favorites", "123") == 6
    assert cache.get_cached_count("favorites", "123") == 6
    
    # Test decrementing counter
    assert cache.decrement_count("favorites", "123") == 5
    assert cache.get_cached_count("favorites", "123") == 5

def test_key_generation():
    assert cache.generate_key(cache.EXERCISE_PREFIX, "123") == "exercise:123"
    assert cache.generate_key(cache.USER_PREFIX, "456") == "user:456"
    assert cache.generate_key(cache.COUNT_PREFIX, "789") == "count:789"

def test_redis_connection():
    is_healthy, message = cache.check_redis_connection()
    assert is_healthy is True
    assert message == "Redis connection is healthy"

def test_cache_error_handling():
    # Test get with invalid JSON
    cache.redis_client.set("test:invalid", "{invalid json}")
    assert cache.cache_get("test:invalid") is None
    
    # Test increment/decrement with non-numeric value
    cache.redis_client.set("test:non-numeric", "not a number")
    assert cache.cache_increment("test:non-numeric") is None
    assert cache.cache_decrement("test:non-numeric") is None 