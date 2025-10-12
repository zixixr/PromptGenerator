from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.models.requests import CreateSessionRequest, SendMessageRequest
from src.models.responses import (
    CreateSessionResponse,
    SendMessageResponse,
    GetHistoryResponse,
    ListSessionsResponse,
    SessionSummary,
    ErrorResponse,
)
from src.services.session_manager import SessionNotFound, SessionManager
from src.services.doubao_client import RateLimitExceeded, ServiceUnavailable
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_session_manager(request: Request) -> SessionManager:
    """Dependency to get session manager from app state."""
    return request.app.state.session_manager


@router.post(
    "/sessions",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def create_session(request_data: CreateSessionRequest, request: Request):
    """Create a new conversation session."""
    try:
        session_manager = get_session_manager(request)
        session = await session_manager.create_session(
            template=request_data.system_prompt_template,
            variables=request_data.variables,
        )
        return CreateSessionResponse(
            session_id=session.session_id,
            resolved_system_prompt=session.resolved_system_prompt,
            created_at=session.created_at,
        )
    except ServiceUnavailable as e:
        return JSONResponse(
            status_code=503,
            content={"error": "ServiceUnavailable", "detail": str(e)},
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "detail": "Internal server error"},
        )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SendMessageResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def send_message(
    session_id: str, request_data: SendMessageRequest, request: Request
):
    """Send a message to a session."""
    try:
        session_manager = get_session_manager(request)
        message_round = await session_manager.send_message(
            session_id=session_id, message=request_data.message
        )
        return SendMessageResponse(
            session_id=session_id,
            round_number=message_round.round_number,
            user_message=message_round.user_message,
            assistant_response=message_round.assistant_response,
            timestamp=message_round.timestamp,
        )
    except SessionNotFound:
        return JSONResponse(
            status_code=404,
            content={
                "error": "SessionNotFound",
                "detail": f"Session {session_id} not found",
                "session_id": session_id,
            },
        )
    except RateLimitExceeded as e:
        return JSONResponse(
            status_code=429,
            content={"error": "RateLimitExceeded", "detail": str(e), "session_id": session_id},
        )
    except ServiceUnavailable as e:
        return JSONResponse(
            status_code=503,
            content={"error": "ServiceUnavailable", "detail": str(e), "session_id": session_id},
        )
    except Exception as e:
        logger.error(f"Error sending message to session {session_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "Internal server error",
                "session_id": session_id,
            },
        )


@router.get(
    "/sessions/{session_id}/history",
    response_model=GetHistoryResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_history(session_id: str, request: Request):
    """Get full history of a session."""
    try:
        session_manager = get_session_manager(request)
        session = await session_manager.get_session(session_id)
        return GetHistoryResponse(
            session_id=session.session_id,
            system_prompt_template=session.system_prompt_template,
            resolved_system_prompt=session.resolved_system_prompt,
            variables=session.variables,
            created_at=session.created_at,
            last_activity=session.last_activity,
            rounds=session.rounds,
        )
    except SessionNotFound:
        return JSONResponse(
            status_code=404,
            content={
                "error": "SessionNotFound",
                "detail": f"Session {session_id} not found",
                "session_id": session_id,
            },
        )
    except Exception as e:
        logger.error(f"Error getting history for session {session_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "Internal server error",
                "session_id": session_id,
            },
        )


@router.get("/sessions", response_model=ListSessionsResponse)
async def list_sessions(request: Request):
    """List all active sessions."""
    try:
        session_manager = get_session_manager(request)
        sessions = await session_manager.list_sessions()
        summaries = [
            SessionSummary(
                session_id=s.session_id,
                created_at=s.created_at,
                last_activity=s.last_activity,
                message_count=len(s.rounds),
            )
            for s in sessions
        ]
        return ListSessionsResponse(sessions=summaries, total=len(summaries))
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "Internal server error",
            },
        )


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_session(session_id: str, request: Request):
    """Delete a session."""
    try:
        session_manager = get_session_manager(request)
        await session_manager.delete_session(session_id)
    except SessionNotFound:
        return JSONResponse(
            status_code=404,
            content={
                "error": "SessionNotFound",
                "detail": f"Session {session_id} not found",
                "session_id": session_id,
            },
        )
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "detail": "Internal server error",
                "session_id": session_id,
            },
        )
