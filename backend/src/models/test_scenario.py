"""TestScenario model - user interaction context for conversation simulation."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class TestScenarioORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for TestScenario."""

    __tablename__ = "test_scenarios"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_user_behavior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    turn_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    project: Mapped["ProjectORM"] = relationship(
        "ProjectORM", back_populates="test_scenarios"
    )
    conversations: Mapped[list["ConversationORM"]] = relationship(
        "ConversationORM", back_populates="test_scenario"
    )


# Pydantic models


class TestScenarioCreate(BaseModel):
    """Schema for creating a test scenario."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=2000)
    expected_user_behavior: Optional[str] = None
    turn_limit: int = Field(..., ge=1, le=50)
    priority: int = Field(default=5, ge=1, le=10)


class TestScenario(BaseModel):
    """Schema for test scenario representation."""

    id: UUID
    name: str
    description: str
    expected_user_behavior: Optional[str] = None
    turn_limit: int
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True


class TestScenarioResponse(TestScenario):
    """Full test scenario response."""

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import ConversationORM
    from .project import ProjectORM
