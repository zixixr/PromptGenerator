import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestDeleteSession:
    """Contract tests for DELETE /sessions/{id} endpoint."""

    def test_delete_session_success(self):
        """Test 204 response for successful deletion."""
        with TestClient(app) as client:
            # Create session
            create_response = client.post(
                "/sessions",
                json={"system_prompt_template": "Test"},
            )
            session_id = create_response.json()["session_id"]

            # Delete session
            response = client.delete(f"/sessions/{session_id}")

        assert response.status_code == 204

    def test_delete_session_not_found_404(self):
        """Test 404 for non-existent session."""
        with TestClient(app) as client:
            response = client.delete("/sessions/nonexistent")

        assert response.status_code == 404

    def test_delete_session_idempotency(self):
        """Test that second delete returns 404."""
        with TestClient(app) as client:
            # Create and delete session
            create_response = client.post(
                "/sessions",
                json={"system_prompt_template": "Test"},
            )
            session_id = create_response.json()["session_id"]
            client.delete(f"/sessions/{session_id}")

            # Try to delete again
            response = client.delete(f"/sessions/{session_id}")

        assert response.status_code == 404
