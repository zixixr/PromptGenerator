import asyncio
import logging
from typing import Dict, List
from datetime import datetime, timezone
from src.models.session import Session, MessageRound
from src.services.template_engine import TemplateEngine
from src.services.doubao_client import DoubaoClient, ServiceUnavailable
from src.services.file_storage import FileStorage
from src.config import settings

logger = logging.getLogger(__name__)


class SessionNotFound(Exception):
    """Raised when session does not exist."""
    pass


class SessionManager:
    """Manages conversation sessions in memory."""

    def __init__(
        self,
        template_engine: TemplateEngine = None,
        doubao_client: DoubaoClient = None,
        file_storage: FileStorage = None,
        max_sessions: int = None,
    ):
        self.sessions: Dict[str, Session] = {}
        self.lock = asyncio.Lock()
        self.template_engine = template_engine or TemplateEngine()
        self.doubao_client = doubao_client or DoubaoClient()
        self.file_storage = file_storage or FileStorage()
        self.max_sessions = max_sessions or settings.MAX_SESSIONS

    async def create_session(self, template: str, variables: Dict[str, str]) -> Session:
        """
        Create a new session.

        Args:
            template: System prompt template
            variables: Variable substitution map

        Returns:
            Created Session object

        Raises:
            ServiceUnavailable: When max capacity reached
        """
        async with self.lock:
            if len(self.sessions) >= self.max_sessions:
                raise ServiceUnavailable(
                    f"Maximum session capacity ({self.max_sessions}) reached. "
                    "Please delete inactive sessions."
                )

            # Render template
            resolved_prompt = self.template_engine.render(template, variables)

            # Create session
            session = Session(
                system_prompt_template=template,
                resolved_system_prompt=resolved_prompt,
                variables=variables,
            )

            self.sessions[session.session_id] = session
            logger.info(f"Created session {session.session_id}")
            return session

    async def get_session(self, session_id: str) -> Session:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object

        Raises:
            SessionNotFound: When session doesn't exist
        """
        session = self.sessions.get(session_id)
        if not session:
            raise SessionNotFound(f"Session {session_id} not found")
        return session

    async def list_sessions(self) -> List[Session]:
        """List all active sessions."""
        return list(self.sessions.values())

    async def delete_session(self, session_id: str) -> None:
        """
        Delete session by ID.

        Args:
            session_id: Session identifier

        Raises:
            SessionNotFound: When session doesn't exist
        """
        async with self.lock:
            if session_id not in self.sessions:
                raise SessionNotFound(f"Session {session_id} not found")
            del self.sessions[session_id]
            logger.info(f"Deleted session {session_id}")

    async def send_message(self, session_id: str, message: str) -> MessageRound:
        """
        Send message to session.

        Args:
            session_id: Session identifier
            message: User message

        Returns:
            MessageRound object

        Raises:
            SessionNotFound: When session doesn't exist
            ServiceUnavailable: When Doubao API fails
        """
        session = await self.get_session(session_id)

        # Ensure single-flight per session to maintain order and avoid race conditions
        async with session.lock:
            # Build context (last 10 rounds)
            context = []
            last_10_rounds = (
                session.rounds[-10:] if len(session.rounds) > 10 else session.rounds
            )
            for round in last_10_rounds:
                context.append({"role": "user", "content": round.user_message})
                context.append({"role": "assistant", "content": round.assistant_response})

            # Call Doubao API
            try:
                assistant_response = await self.doubao_client.send_message(
                    system_prompt=session.resolved_system_prompt,
                    context=context,
                    user_message=message,
                )
            except Exception as e:
                logger.error(f"Doubao API error for session {session_id}: {e}")
                raise

            # Create message round
            round_number = len(session.rounds) + 1
            message_round = MessageRound(
                round_number=round_number,
                user_message=message,
                assistant_response=assistant_response,
            )

            # Update session
            session.rounds.append(message_round)
            session.last_activity = datetime.now(timezone.utc)

            # Save history (async, non-blocking)
            asyncio.create_task(self.file_storage.save_history(session))

            logger.info(f"Session {session_id} round {round_number} completed")
            return message_round
