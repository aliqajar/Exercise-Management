from pydantic import BaseModel, conint, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshToken(BaseModel):
    refresh_token: str

# Exercise schemas
class ExerciseBase(BaseModel):
    name: str
    description: str
    difficulty_level: conint(ge=1, le=5)  # Validates integer between 1 and 5
    is_public: bool = True

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[conint(ge=1, le=5)] = None
    is_public: Optional[bool] = None

class Exercise(ExerciseBase):
    id: str
    creator_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    favorite_count: Optional[int] = 0
    save_count: Optional[int] = 0
    user_rating: Optional[float] = None
    is_favorited: Optional[bool] = False
    is_saved: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

# Rating schema
class RatingCreate(BaseModel):
    value: int = Field(ge=1, le=5)

class Rating(BaseModel):
    id: UUID
    value: int
    exercise_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Response schemas
class ExerciseList(BaseModel):
    exercises: List[Exercise]
    total: int
    page: int
    per_page: int

class Message(BaseModel):
    message: str

# Health Check Response
class RedisHealth(BaseModel):
    status: str
    message: str
    timestamp: datetime

class HealthCheck(BaseModel):
    status: str
    redis_status: RedisHealth
    timestamp: datetime 