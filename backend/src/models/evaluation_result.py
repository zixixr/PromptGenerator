"""EvaluationResult model - scores and explanations for conversations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class EvaluationResultORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for EvaluationResult."""

    __tablename__ = "evaluation_results"

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, unique=True
    )
    criterion_scores: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False
    )  # Map of criterion_id -> {score, explanation}
    aggregate_score: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evaluator_model: Mapped[str] = mapped_column(String(100), nullable=False)
    evaluation_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    conversation: Mapped["ConversationORM"] = relationship(
        "ConversationORM", back_populates="evaluation_result"
    )


# Pydantic models


class CriterionScore(BaseModel):
    """Schema for individual criterion score."""

    score: float
    explanation: str


class EvaluationResult(BaseModel):
    """Schema for evaluation result representation."""

    id: UUID
    conversation_id: UUID
    criterion_scores: dict[str, CriterionScore]
    aggregate_score: float
    passed: bool
    evaluated_at: datetime
    evaluator_model: str
    evaluation_duration_seconds: float

    class Config:
        from_attributes = True


class EvaluationResultResponse(EvaluationResult):
    """Full evaluation result response."""

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import ConversationORM
