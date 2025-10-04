"""EvaluationCriterion model - scoring dimension definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class EvaluationCriterionORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for EvaluationCriterion."""

    __tablename__ = "evaluation_criteria"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    is_predefined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scoring_rubric: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["ProjectORM"] = relationship(
        "ProjectORM", back_populates="evaluation_criteria"
    )


# Pydantic models


class EvaluationCriterionCreate(BaseModel):
    """Schema for creating an evaluation criterion."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    threshold: float = Field(..., ge=0.0, le=100.0)
    is_predefined: bool = False
    scoring_rubric: Optional[str] = None
    is_enabled: bool = True

    def validate_custom_rubric(self) -> None:
        """Validate that custom criteria have scoring rubrics."""
        if not self.is_predefined and not self.scoring_rubric:
            raise ValueError("Custom criteria must have a scoring_rubric")


class EvaluationCriterion(BaseModel):
    """Schema for evaluation criterion representation."""

    id: UUID
    name: str
    description: str
    threshold: float
    is_predefined: bool
    scoring_rubric: Optional[str] = None
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationCriterionResponse(EvaluationCriterion):
    """Full evaluation criterion response."""

    class Config:
        from_attributes = True


# Predefined criteria names
PREDEFINED_CRITERIA = {
    "persona_consistency": "How well responses match defined persona",
    "tone_style": "Appropriate tone for context",
    "factual_accuracy": "Correctness of information",
    "engagement_quality": "Conversational quality and helpfulness",
    "safety_compliance": "Adherence to safety policies",
}


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project import ProjectORM
