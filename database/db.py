"""
Database connection and session management
Supports PostgreSQL (production) and SQLite (local development)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database URL - PostgreSQL for production, SQLite for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./proposal_generator.db"
)

# Convert PostgreSQL URL format if needed (Render uses postgres://, SQLAlchemy needs postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Engine configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("SQL_ECHO", "False").lower() == "true"
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before using
        echo=os.getenv("SQL_ECHO", "False").lower() == "true"
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Use in FastAPI/Flask route handlers
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """
    Get a new database session
    Use for standalone operations
    
    Returns:
        Database session
    """
    return SessionLocal()


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    from database.models import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def close_db():
    """Close database connections"""
    engine.dispose()
    logger.info("Database connections closed")

