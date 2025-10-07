import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestGetHistory:
    """Contract tests for GET /sessions/{id}/history endpoint."""

    def test_get_history_success(self):
        """Test 200 response with full session data."""
        with TestClient(app) as client:
            # Create session
            create_response = client.post(
                "/sessions",
                json={
                    "system_prompt_template": "You are a {{role}} assistant.",
                    "variables": {"role": "helpful"},
                },
            )
            session_id = create_response.json()["session_id"]

            # Get history
            response = client.get(f"/sessions/{session_id}/history")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["system_prompt_template"] == "You are a {{role}} assistant."
        assert data["resolved_system_prompt"] == "You are a helpful assistant."
        assert data["variables"] == {"role": "helpful"}
        assert "created_at" in data
        assert "last_activity" in data
        assert data["rounds"] == []  # No messages yet

    def test_get_history_not_found_404(self):
        """Test 404 for non-existent session."""
        with TestClient(app) as client:
            response = client.get("/sessions/nonexistent/history")

        assert response.status_code == 404
