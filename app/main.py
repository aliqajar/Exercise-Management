from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, create_tables
from .routers import exercises, users, auth, health
from . import schemas, cache
from datetime import datetime

# Create all tables on startup
create_tables()

app = FastAPI(
    title="Exercise Management API",
    description="""
    A RESTful API for managing exercises with authentication and social features.
    
    Features:
    * User authentication with JWT
    * Exercise creation and management
    * Public and private exercises
    * Social features (favorites, saves, ratings)
    * Caching for improved performance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(health.router, prefix="/health", tags=["Health"]) 