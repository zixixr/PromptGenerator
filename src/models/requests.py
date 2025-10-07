from pydantic import BaseModel, Field, field_validator
from typing import Dict


class CreateSessionRequest(BaseModel):
    """Request model for creating a new session."""

    system_prompt_template: str = Field(..., min_length=1, description="System prompt template")
    variables: Dict[str, str] = Field(default_factory=dict, description="Variable substitution map")

    @field_validator("system_prompt_template")
    @classmethod
    def validate_template_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("system_prompt_template cannot be empty or whitespace")
        return v


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""

    message: str = Field(..., min_length=1, description="User message")

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("message cannot be empty or whitespace-only")
        return v.strip()
