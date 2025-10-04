"""Conversation model - multi-turn dialogue with evaluations."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TRUNCATED = "truncated"  # Reached turn limit before natural completion


class ConversationORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for Conversation."""

    __tablename__ = "conversations"

    iteration_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("iterations.id"), nullable=False
    )
    test_scenario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("test_scenarios.id"), nullable=False
    )
    turns: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)  # Array of turn objects
    turn_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    iteration: Mapped["IterationORM"] = relationship(
        "IterationORM", back_populates="conversations"
    )
    test_scenario: Mapped["TestScenarioORM"] = relationship(
        "TestScenarioORM", back_populates="conversations"
    )
    evaluation_result: Mapped[Optional["EvaluationResultORM"]] = relationship(
        "EvaluationResultORM", back_populates="conversation", uselist=False
    )


# Pydantic models


class ConversationTurn(BaseModel):
    """Schema for a single conversation turn."""

    role: str  # "user" or "assistant"
    message: str
    timestamp: datetime


class Conversation(BaseModel):
    """Schema for conversation representation."""

    id: UUID
    iteration_id: UUID
    test_scenario_id: UUID
    turn_count: int
    status: ConversationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationResponse(Conversation):
    """Conversation response with evaluation."""

    test_scenario_name: str
    evaluation_result: Optional["EvaluationResultResponse"] = None

    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    """Detailed conversation view with full transcript."""

    turns: list[ConversationTurn] = []
    metadata: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .evaluation_result import EvaluationResultORM, EvaluationResultResponse
    from .iteration import IterationORM
    from .test_scenario import TestScenarioORM
