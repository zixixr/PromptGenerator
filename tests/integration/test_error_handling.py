"""Integration test: Error handling."""
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch


@pytest.mark.asyncio
async def test_empty_message_error(client: AsyncClient, test_session_id: str):
    """Test empty message returns 400."""
    response = await client.post(
        f"/sessions/{test_session_id}/messages",
        json={"message": ""}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "detail" in data


@pytest.mark.asyncio
async def test_session_not_found_error(client: AsyncClient):
    """Test session not found returns 404."""
    # Try to send message to non-existent session
    response = await client.post(
        "/sessions/nonexistent123/messages",
        json={"message": "Hello"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"] == "SessionNotFound"
    assert "session_id" in data


@pytest.mark.asyncio
async def test_capacity_limit_error(client: AsyncClient):
    """Test creating 51 sessions, expect 503 on 51st."""
    # Create 50 sessions
    session_ids = []
    for i in range(50):
        response = await client.post(
            "/sessions",
            json={"system_prompt_template": f"Session {i}"}
        )
        if response.status_code == status.HTTP_201_CREATED:
            session_ids.append(response.json()["session_id"])

    # 51st session should fail
    response = await client.post(
        "/sessions",
        json={"system_prompt_template": "Session 51"}
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()
    assert "error" in data
    assert "detail" in data

    # Cleanup
    for sid in session_ids:
        await client.delete(f"/sessions/{sid}")


@pytest.mark.asyncio
async def test_doubao_timeout_error(client: AsyncClient, test_session_id: str):
    """Test Doubao API timeout (mock 6-second timeout, expect 503)."""
    with patch("src.services.doubao_client.DoubaoClient.send_message") as mock_send:
        import asyncio
        from src.services.doubao_client import ServiceUnavailable

        # Simulate timeout
        async def timeout_mock(*args, **kwargs):
            await asyncio.sleep(7)  # Longer than 6-second timeout
            raise ServiceUnavailable("Connection timeout after 6 seconds")

        mock_send.side_effect = timeout_mock

        response = await client.post(
            f"/sessions/{test_session_id}/messages",
            json={"message": "This will timeout"}
        )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert "error" in data
        assert "detail" in data
        assert "session_id" in data


@pytest.mark.asyncio
async def test_error_response_includes_required_fields(client: AsyncClient):
    """Test error responses include error, detail, session_id fields."""
    # Create session and delete it
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "Test"}
    )
    session_id = create_response.json()["session_id"]
    await client.delete(f"/sessions/{session_id}")

    # Try to access deleted session
    response = await client.get(f"/sessions/{session_id}/history")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()

    # Validate error response structure
    assert "error" in data
    assert isinstance(data["error"], str)

    assert "detail" in data
    assert isinstance(data["detail"], str)

    assert "session_id" in data
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_validation_error_empty_template(client: AsyncClient):
    """Test validation error for empty system_prompt_template."""
    response = await client.post(
        "/sessions",
        json={"system_prompt_template": ""}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "error" in data
    assert "detail" in data


@pytest.mark.asyncio
async def test_rate_limit_error(client: AsyncClient, test_session_id: str):
    """Test Doubao rate limit error handling."""
    with patch("src.services.doubao_client.DoubaoClient.send_message") as mock_send:
        from src.services.doubao_client import RateLimitExceeded
        mock_send.side_effect = RateLimitExceeded("Rate limit exceeded")

        response = await client.post(
            f"/sessions/{test_session_id}/messages",
            json={"message": "Test message"}
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        data = response.json()
        assert data["error"] == "RateLimitExceeded"
        assert "detail" in data
