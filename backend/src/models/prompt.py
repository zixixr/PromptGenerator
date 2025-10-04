"""Prompt model - versioned prompt text with metadata."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class GenerationMethod(str, Enum):
    """Prompt generation method enumeration."""

    INITIAL = "initial"
    LLM_REWRITE = "llm_rewrite"
    MANUAL_EDIT = "manual_edit"


class PromptORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for Prompt."""

    __tablename__ = "prompts"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("prompts.id"), nullable=True
    )
    iteration_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("iterations.id"), nullable=False
    )
    generation_method: Mapped[str] = mapped_column(String(20), nullable=False)
    rewrite_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    iteration: Mapped["IterationORM"] = relationship("IterationORM", back_populates="prompt")
    parent: Mapped[Optional["PromptORM"]] = relationship(
        "PromptORM", remote_side="PromptORM.id", backref="children"
    )


# Pydantic models


class Prompt(BaseModel):
    """Schema for prompt representation."""

    id: UUID
    text: str = Field(..., min_length=1, max_length=50000)
    parent_id: Optional[UUID] = None
    generation_method: GenerationMethod
    rewrite_rationale: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PromptResponse(Prompt):
    """Full prompt response."""

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .iteration import IterationORM
