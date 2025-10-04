"""Database initialization and session management.

Provides SQLite connection, session factory, and table creation.
"""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.base import Base

# Import all models to ensure they're registered with Base
from ..models.project import ProjectORM
from ..models.iteration import IterationORM
from ..models.prompt import PromptORM
from ..models.test_scenario import TestScenarioORM
from ..models.evaluation_criterion import EvaluationCriterionORM
from ..models.conversation import ConversationORM
from ..models.evaluation_result import EvaluationResultORM
from ..models.model_configuration import ModelConfigurationORM

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/prompt_optimizer.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging during development
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database by creating all tables.

    This should be called once at application startup.
    """
    # Ensure data directory exists
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_session() -> Generator[Session, None, None]:
    """Get database session (dependency injection for FastAPI).

    Yields:
        Database session that automatically closes after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables() -> None:
    """Drop all tables (use with caution, mainly for testing)."""
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped")


def reset_database() -> None:
    """Reset database by dropping and recreating all tables."""
    drop_all_tables()
    init_db()
    print("Database reset successfully")
