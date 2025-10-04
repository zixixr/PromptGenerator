"""Integration test: Create and configure new project.

Test Scenario 1 from quickstart.md:
User creates a project with target model, criteria, and test scenarios.
System generates project ID, displays configuration, and sets status to 'draft'.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_configure_project(client: AsyncClient, db_session) -> None:
    """Test creating a new optimization project with full configuration."""
    # Step 1: Create project
    project_payload = {
        "name": "Customer Service Bot Optimization",
        "target_model": "claude-3-5-sonnet",
        "initial_prompt": "You are a helpful customer service assistant.",
        "persona_description": "Friendly and professional customer service representative",
        "max_iterations": 20,
        "model_configuration": {
            "provider": "anthropic",
            "model_name": "claude-3-5-sonnet",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "test_scenarios": [
            {
                "name": "Angry Customer",
                "description": "User is frustrated about delayed order",
                "turn_limit": 5,
                "priority": 5,
            },
            {
                "name": "Product Inquiry",
                "description": "User asks about product features",
                "turn_limit": 4,
                "priority": 5,
            },
            {
                "name": "Refund Request",
                "description": "User wants to return an item",
                "turn_limit": 6,
                "priority": 5,
            },
        ],
        "evaluation_criteria": [
            {
                "name": "Persona Consistency",
                "description": "Responses match customer service persona",
                "threshold": 85.0,
                "is_predefined": True,
                "is_enabled": True,
            },
            {
                "name": "Safety Compliance",
                "description": "No harmful or inappropriate content",
                "threshold": 100.0,
                "is_predefined": True,
                "is_enabled": True,
            },
        ],
    }

    response = await client.post("/api/projects", json=project_payload)

    # Assertions from quickstart.md verification steps
    assert response.status_code == 201
    data = response.json()

    # 1. Generate unique project ID (UUID format)
    assert "id" in data
    import uuid

    try:
        uuid.UUID(data["id"])
    except ValueError:
        pytest.fail("Project ID is not a valid UUID")

    # 2. Display project configuration summary
    assert data["name"] == "Customer Service Bot Optimization"
    assert data["target_model"] == "claude-3-5-sonnet"
    assert len(data["test_scenarios"]) == 3
    assert len(data["evaluation_criteria"]) == 2
    assert data["max_iterations"] == 20
    assert data["status"] == "draft"

    # 3. Verify project persisted to database
    project_id = data["id"]
    get_response = await client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 200

    # 4. Verify project appears in list
    list_response = await client.get("/api/projects")
    assert list_response.status_code == 200
    projects = list_response.json()["projects"]
    assert any(p["id"] == project_id for p in projects)


@pytest.fixture
async def client() -> AsyncClient:
    """Create test HTTP client."""
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def db_session():
    """Create database session for testing."""
    from src.storage.db import get_session

    session = get_session()
    try:
        yield session
    finally:
        session.close()
