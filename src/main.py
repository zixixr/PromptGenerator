from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
from src.routes import chat_api
from src.services.session_manager import SessionManager
from src.logging_config import setup_logging
from src.config import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Chat Service with Doubao Seed 1.6",
    version="1.0.0",
    description="Conversation service with 10-round context window and Mustache templates",
)

# Include routers
app.include_router(chat_api.router)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info("Starting AI Chat Service")
    
    # Create conversations directory
    conversations_dir = Path(settings.CONVERSATIONS_DIR)
    conversations_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Conversations directory: {conversations_dir.absolute()}")
    
    # Initialize session manager
    app.state.session_manager = SessionManager()
    logger.info(f"Session manager initialized (max sessions: {settings.MAX_SESSIONS})")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # TODO: Add actual Doubao connectivity check
    return JSONResponse(
        content={
            "status": "ok",
            "doubao_connected": True,  # Placeholder
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": "An unexpected error occurred"},
    )
