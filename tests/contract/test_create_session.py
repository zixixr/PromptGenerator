import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestCreateSession:
    """Contract tests for POST /sessions endpoint."""

    def test_create_session_success(self):
        """Test 201 response with session_id, resolved_system_prompt, created_at."""
        with TestClient(app) as client:
            response = client.post(
                "/sessions",
                json={
                    "system_prompt_template": "You are a {{role}} assistant.",
                    "variables": {"role": "helpful"},
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "resolved_system_prompt" in data
        assert "created_at" in data
        assert data["resolved_system_prompt"] == "You are a helpful assistant."
        assert len(data["session_id"]) == 32  # UUID hex format

    def test_create_session_no_variables(self):
        """Test creating session with plain text system prompt (no variables)."""
        with TestClient(app) as client:
            response = client.post(
                "/sessions",
                json={"system_prompt_template": "You are a helpful assistant."},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["resolved_system_prompt"] == "You are a helpful assistant."

    def test_create_session_empty_template_400(self):
        """Test 400 for empty system_prompt_template."""
        with TestClient(app) as client:
            response = client.post("/sessions", json={"system_prompt_template": ""})

        assert response.status_code == 422 or response.status_code == 400

    def test_create_session_missing_template_400(self):
        """Test 400 when system_prompt_template is missing."""
        with TestClient(app) as client:
            response = client.post("/sessions", json={"variables": {"role": "helpful"}})

        assert response.status_code == 422 or response.status_code == 400
