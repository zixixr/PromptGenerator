"""ModelConfiguration model - target LLM settings."""

from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin


class LLMProvider(str, Enum):
    """LLM provider enumeration."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class ModelConfigurationORM(Base, UUIDMixin):
    """SQLAlchemy ORM model for ModelConfiguration."""

    __tablename__ = "model_configurations"

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False, unique=True
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    additional_params: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    project: Mapped["ProjectORM"] = relationship(
        "ProjectORM", back_populates="model_configuration"
    )


# Pydantic models


class ModelConfigurationCreate(BaseModel):
    """Schema for creating model configuration."""

    provider: LLMProvider
    model_name: str = Field(..., min_length=1)
    api_endpoint: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=128000)
    additional_params: Optional[dict[str, Any]] = None

    def validate_custom_endpoint(self) -> None:
        """Validate that custom providers have an endpoint."""
        if self.provider == LLMProvider.CUSTOM and not self.api_endpoint:
            raise ValueError("Custom provider requires api_endpoint")


class ModelConfiguration(BaseModel):
    """Schema for model configuration representation."""

    id: UUID
    provider: LLMProvider
    model_name: str
    api_endpoint: Optional[str] = None
    temperature: float
    max_tokens: int
    additional_params: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class ModelConfigurationResponse(ModelConfiguration):
    """Full model configuration response."""

    class Config:
        from_attributes = True


# Forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .project import ProjectORM
