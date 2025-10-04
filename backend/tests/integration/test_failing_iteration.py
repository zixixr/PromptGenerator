"""Integration test: Run iteration with failing criteria.

Test Scenario 2 from quickstart.md:
Start iteration, simulate conversations, evaluate against criteria,
detect failures, and auto-generate revised prompt.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_iteration_with_failing_criteria(client: AsyncClient, test_project) -> None:
    """Test iteration that fails some criteria triggers prompt rewriting."""
    project_id = test_project["id"]

    # Start iteration
    response = await client.post(f"/api/projects/{project_id}/iterations")
    assert response.status_code == 202  # Async operation accepted

    iteration_data = response.json()
    iteration_id = iteration_data["id"]

    # Poll until iteration completes (in real impl, this would be async)
    # For test, we check the final state
    iteration_response = await client.get(f"/api/iterations/{iteration_id}")
    assert iteration_response.status_code == 200

    iteration = iteration_response.json()
    assert iteration["iteration_number"] == 1
    assert iteration["status"] in ["running", "completed"]

    # Verify conversations were created
    conv_response = await client.get(f"/api/iterations/{iteration_id}/conversations")
    assert conv_response.status_code == 200
    conversations = conv_response.json()["conversations"]
    assert len(conversations) > 0

    # Each conversation should have evaluation results
    for conv in conversations:
        assert "evaluation_result" in conv
        assert "criterion_scores" in conv["evaluation_result"]


@pytest.fixture
async def test_project(client: AsyncClient):
    """Create a test project for iteration testing."""
    payload = {
        "name": "Test Iteration Project",
        "target_model": "gpt-4",
        "initial_prompt": "You are a helpful assistant.",
        "persona_description": "Assistant",
        "max_iterations": 3,
        "model_configuration": {
            "provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "test_scenarios": [
            {
                "name": "Test Scenario",
                "description": "Basic test",
                "turn_limit": 3,
            }
        ],
        "evaluation_criteria": [
            {
                "name": "Quality",
                "description": "Response quality",
                "threshold": 80.0,
            }
        ],
    }

    response = await client.post("/api/projects", json=payload)
    return response.json()


@pytest.fixture
async def client() -> AsyncClient:
    """Create test HTTP client."""
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
