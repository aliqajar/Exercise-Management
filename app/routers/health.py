from fastapi import APIRouter, Depends
from datetime import datetime
from app.schemas import HealthCheck, RedisHealth
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import cache

router = APIRouter()

@router.get("", response_model=HealthCheck)
async def check_health(db: Session = Depends(get_db)):
    """
    Check the health status of the application and its dependencies
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check Redis connection
        is_healthy, message = cache.check_redis_connection()
        redis_health = RedisHealth(
            status="healthy" if is_healthy else "unhealthy",
            message=message,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        redis_health = RedisHealth(
            status="unhealthy",
            message=str(e),
            timestamp=datetime.utcnow()
        )
    
    return HealthCheck(
        status="healthy",
        redis_status=redis_health,
        timestamp=datetime.utcnow()
    )

@router.get("/redis", response_model=RedisHealth)
async def check_redis_health():
    """
    Check Redis connection health specifically
    """
    is_healthy, message = cache.check_redis_connection()
    return RedisHealth(
        status="healthy" if is_healthy else "unhealthy",
        message=message,
        timestamp=datetime.utcnow()
    ) 