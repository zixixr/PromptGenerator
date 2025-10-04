"""FastAPI application entry point.

This is a minimal stub that will be expanded with routes and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .storage.db import init_db

# Create FastAPI application
app = FastAPI(
    title="Prompt Optimizer API",
    description="Automated prompt iteration system backend",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    init_db()


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "prompt-optimizer-backend"}


# Include API routes
from .api import credentials_router, iterations_router, projects_router

app.include_router(projects_router, prefix="/api", tags=["projects"])
app.include_router(iterations_router, prefix="/api", tags=["iterations"])
app.include_router(credentials_router, prefix="/api", tags=["credentials"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
