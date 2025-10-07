from datetime import datetime, timezone
from typing import Dict, List
from pydantic import BaseModel, Field
import uuid
import asyncio


class MessageRound(BaseModel):
    """Represents one complete user-assistant exchange."""

    round_number: int = Field(..., ge=1, description="Sequential round number starting at 1")
    user_message: str = Field(..., min_length=1, description="User's message")
    assistant_response: str = Field(..., description="Assistant's response from Doubao")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Session(BaseModel):
    """Represents an active conversation session."""

    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    system_prompt_template: str = Field(..., min_length=1)
    resolved_system_prompt: str = Field(...)
    variables: Dict[str, str] = Field(default_factory=dict)
    rounds: List[MessageRound] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize message queue (not serialized)
        self._message_queue = asyncio.Queue()

    @property
    def message_queue(self):
        """Get the message queue for this session."""
        if not hasattr(self, "_message_queue"):
            self._message_queue = asyncio.Queue()
        return self._message_queue
