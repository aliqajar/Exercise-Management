from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, func, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    exercises = relationship("Exercise", back_populates="creator", foreign_keys="Exercise.creator_id", cascade="all, delete-orphan")
    favorite_exercises = relationship("Exercise", secondary="favorites", back_populates="favorited_by", cascade="all, delete")
    saved_exercises = relationship("Exercise", secondary="saves", back_populates="saved_by", cascade="all, delete")
    ratings = relationship("Rating", back_populates="user", foreign_keys="Rating.user_id", cascade="all, delete-orphan")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    difficulty_level = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=True)
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="exercises", foreign_keys=[creator_id], passive_deletes=True)
    favorited_by = relationship("User", secondary="favorites", back_populates="favorite_exercises", cascade="all, delete")
    saved_by = relationship("User", secondary="saves", back_populates="saved_exercises", cascade="all, delete")
    ratings = relationship("Rating", back_populates="exercise", foreign_keys="Rating.exercise_id", cascade="all, delete-orphan")

    # Multi-column index for efficient filtering and sorting
    __table_args__ = (
        Index('idx_exercise_search', 'is_public', 'difficulty_level', 'name'),
    )

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id = Column(String(36), ForeignKey("exercises.id", ondelete="CASCADE"))
    value = Column(Integer, CheckConstraint('value >= 1 AND value <= 5'))  # 1-5
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ratings", foreign_keys=[user_id])
    exercise = relationship("Exercise", back_populates="ratings", foreign_keys=[exercise_id])

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id = Column(String(36), ForeignKey("exercises.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", overlaps="favorite_exercises,favorited_by")
    exercise = relationship("Exercise", overlaps="favorite_exercises,favorited_by")

class Save(Base):
    __tablename__ = "saves"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id = Column(String(36), ForeignKey("exercises.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", overlaps="saved_exercises,saved_by")
    exercise = relationship("Exercise", overlaps="saved_exercises,saved_by") 