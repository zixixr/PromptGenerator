"""Iteration model - represents a single optimization cycle."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class IterationStatus(str, Enum):
    """Iteration status enumeration."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IterationORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for Iteration."""

    __tablename__ = "iterations"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    iteration_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("prompts.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passed_criteria_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_criteria_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    all_criteria_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    project: Mapped["ProjectORM"] = relationship("ProjectORM", back_populates="iterations")
    prompt: Mapped["PromptORM"] = relationship("PromptORM", back_populates="iteration")
    conversations: Mapped[list["ConversationORM"]] = relationship(
        "ConversationORM", back_populates="iteration", cascade="all, delete-orphan"
    )


# Pydantic models


class Iteration(BaseModel):
    """Schema for iteration representation."""

    id: UUID
    project_id: UUID
    iteration_number: int
    status: IterationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    passed_criteria_count: int
    total_criteria_count: int
    all_criteria_passed: bool

    class Config:
        from_attributes = True


class IterationResponse(Iteration):
    """Full iteration response including prompt."""

    prompt: Optional["PromptResponse"] = None

    class Config:
        from_attributes = True


class IterationDetail(IterationResponse):
    """Detailed iteration view with conversations."""

    conversations: list["ConversationResponse"] = []
    aggregated_scores: dict[str, dict[str, float]] = {}

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import ConversationORM, ConversationResponse
    from .project import ProjectORM
    from .prompt import PromptORM, PromptResponse
