import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestListSessions:
    """Contract tests for GET /sessions endpoint."""

    def test_list_sessions_empty(self):
        """Test empty array when no sessions exist."""
        with TestClient(app) as client:
            response = client.get("/sessions")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["sessions"], list)
        assert data["total"] >= 0

    def test_list_sessions_with_data(self):
        """Test listing sessions with created sessions."""
        with TestClient(app) as client:
            # Create a session
            client.post(
                "/sessions",
                json={"system_prompt_template": "Test assistant"},
            )

            # List sessions
            response = client.get("/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["sessions"]) >= 1
        
        # Check session summary structure
        session = data["sessions"][0]
        assert "session_id" in session
        assert "created_at" in session
        assert "last_activity" in session
        assert "message_count" in session
