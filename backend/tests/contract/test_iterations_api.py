"""Contract tests for Iterations API endpoints.

Validates iterations-api.yaml OpenAPI specification:
- GET /api/iterations/{id}
- GET /api/iterations/{id}/conversations
- GET /api/conversations/{id}
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_iteration_contract(client: AsyncClient) -> None:
    """Test GET /api/iterations/{id} contract."""
    iteration_id = uuid4()
    response = await client.get(f"/api/iterations/{iteration_id}")

    # Should return 404 for non-existent iteration
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "status_code" in data


@pytest.mark.asyncio
async def test_list_conversations_contract(client: AsyncClient) -> None:
    """Test GET /api/iterations/{id}/conversations contract."""
    iteration_id = uuid4()
    response = await client.get(f"/api/iterations/{iteration_id}/conversations")

    # Should return 404 for non-existent iteration
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_get_conversation_contract(client: AsyncClient) -> None:
    """Test GET /api/conversations/{id} contract."""
    conversation_id = uuid4()
    response = await client.get(f"/api/conversations/{conversation_id}")

    # Should return 404 for non-existent conversation
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "detail" in data or "error" in data


@pytest.fixture
async def client() -> AsyncClient:
    """Create test HTTP client."""
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
