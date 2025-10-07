from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from src.models.session import MessageRound


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""

    session_id: str
    resolved_system_prompt: str
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SendMessageResponse(BaseModel):
    """Response model for sending a message."""

    session_id: str
    round_number: int
    user_message: str
    assistant_response: str
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class GetHistoryResponse(BaseModel):
    """Response model for getting session history."""

    session_id: str
    system_prompt_template: str
    resolved_system_prompt: str
    variables: dict
    created_at: datetime
    last_activity: datetime
    rounds: List[MessageRound]

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SessionSummary(BaseModel):
    """Summary of a session for list endpoint."""

    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ListSessionsResponse(BaseModel):
    """Response model for listing sessions."""

    sessions: List[SessionSummary]
    total: int


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str
    session_id: Optional[str] = None
