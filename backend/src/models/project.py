"""Project model - represents a prompt optimization session."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class ProjectORM(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy ORM model for Project."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_model: Mapped[str] = mapped_column(String(100), nullable=False)
    initial_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    persona_description: Mapped[str] = mapped_column(Text, nullable=False)
    max_iterations: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    best_iteration_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("iterations.id"), nullable=True
    )

    # Relationships
    test_scenarios: Mapped[list["TestScenarioORM"]] = relationship(
        "TestScenarioORM", back_populates="project", cascade="all, delete-orphan"
    )
    evaluation_criteria: Mapped[list["EvaluationCriterionORM"]] = relationship(
        "EvaluationCriterionORM", back_populates="project", cascade="all, delete-orphan"
    )
    iterations: Mapped[list["IterationORM"]] = relationship(
        "IterationORM", back_populates="project", cascade="all, delete-orphan"
    )
    model_configuration: Mapped["ModelConfigurationORM"] = relationship(
        "ModelConfigurationORM", back_populates="project", cascade="all, delete-orphan"
    )


# Pydantic models for API serialization


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_model: str = Field(..., min_length=1)
    initial_prompt: str = Field(..., min_length=1, max_length=10000)
    persona_description: str = Field(..., min_length=1)
    max_iterations: int = Field(default=20, ge=1, le=100)

    @field_validator("max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int) -> int:
        """Validate max_iterations is within acceptable range."""
        if not 1 <= v <= 100:
            raise ValueError("max_iterations must be between 1 and 100")
        return v


class Project(BaseModel):
    """Schema for project representation."""

    id: UUID
    name: str
    description: Optional[str] = None
    target_model: str
    initial_prompt: str
    persona_description: str
    max_iterations: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    best_iteration_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ProjectResponse(Project):
    """Full project response including relationships."""

    test_scenarios: list["TestScenarioResponse"] = []
    evaluation_criteria: list["EvaluationCriterionResponse"] = []
    model_configuration: Optional["ModelConfigurationResponse"] = None

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    """Summary view of a project for list endpoints."""

    id: UUID
    name: str
    status: ProjectStatus
    created_at: datetime
    iteration_count: int = 0
    best_score: Optional[float] = None

    class Config:
        from_attributes = True


# Forward references - will be resolved when other models are imported
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .evaluation_criterion import EvaluationCriterionORM, EvaluationCriterionResponse
    from .iteration import IterationORM
    from .model_configuration import ModelConfigurationORM, ModelConfigurationResponse
    from .test_scenario import TestScenarioORM, TestScenarioResponse
