"""Contract tests for Projects API endpoints.

Validates projects-api.yaml OpenAPI specification:
- POST /api/projects
- GET /api/projects
- GET /api/projects/{id}
- DELETE /api/projects/{id}
- POST /api/projects/{id}/iterations
- POST /api/projects/{id}/export
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_project_contract(client: AsyncClient) -> None:
    """Test POST /api/projects contract (projects-api.yaml)."""
    payload = {
        "name": "Test Project",
        "description": "Test description",
        "target_model": "gpt-4",
        "initial_prompt": "You are a helpful assistant.",
        "persona_description": "Customer service bot",
        "max_iterations": 20,
        "model_configuration": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "test_scenarios": [
            {
                "name": "Angry Customer",
                "description": "User is frustrated",
                "turn_limit": 5,
                "priority": 5,
            }
        ],
        "evaluation_criteria": [
            {
                "name": "Persona Consistency",
                "description": "Matches defined persona",
                "threshold": 85.0,
                "is_predefined": True,
                "is_enabled": True,
            }
        ],
    }

    response = await client.post("/api/projects", json=payload)

    # Contract assertions
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Project"
    assert data["target_model"] == "gpt-4"
    assert data["status"] == "draft"
    assert data["max_iterations"] == 20
    assert len(data["test_scenarios"]) == 1
    assert len(data["evaluation_criteria"]) == 1


@pytest.mark.asyncio
async def test_list_projects_contract(client: AsyncClient) -> None:
    """Test GET /api/projects contract."""
    response = await client.get("/api/projects")

    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert isinstance(data["projects"], list)
    assert isinstance(data["total"], int)


@pytest.mark.asyncio
async def test_get_project_contract(client: AsyncClient) -> None:
    """Test GET /api/projects/{id} contract."""
    project_id = uuid4()
    response = await client.get(f"/api/projects/{project_id}")

    # Should return 404 for non-existent project
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_delete_project_contract(client: AsyncClient) -> None:
    """Test DELETE /api/projects/{id} contract."""
    project_id = uuid4()
    response = await client.delete(f"/api/projects/{project_id}")

    # Should return 404 for non-existent project
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_start_iteration_contract(client: AsyncClient) -> None:
    """Test POST /api/projects/{id}/iterations contract."""
    project_id = uuid4()
    response = await client.post(f"/api/projects/{project_id}/iterations")

    # Should return 404 for non-existent project
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_export_report_contract(client: AsyncClient) -> None:
    """Test POST /api/projects/{id}/export contract."""
    project_id = uuid4()
    payload = {"format": "json"}

    response = await client.post(f"/api/projects/{project_id}/export", json=payload)

    # Should return 404 for non-existent project
    assert response.status_code == 404


@pytest.fixture
async def client() -> AsyncClient:
    """Create test HTTP client."""
    # This will be implemented when we create the FastAPI app
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
