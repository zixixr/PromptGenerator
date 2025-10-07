import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app


class TestSendMessage:
    """Contract tests for POST /sessions/{id}/messages endpoint."""

    @patch('src.services.doubao_client.DoubaoClient.send_message')
    def test_send_message_success(self, mock_send):
        """Test 200 response with message round details."""
        mock_send.return_value = AsyncMock(return_value="This is a test response")()
        
        # First create a session
        with TestClient(app) as client:
            create_response = client.post(
                "/sessions",
                json={"system_prompt_template": "You are a helpful assistant."},
            )
            session_id = create_response.json()["session_id"]

            # Mock the Doubao client response
            with patch.object(app.state.session_manager.doubao_client, 'send_message', 
                            new_callable=AsyncMock, return_value="This is a test response"):
                # Send message
                response = client.post(
                    f"/sessions/{session_id}/messages",
                    json={"message": "Hello, how are you?"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["round_number"] == 1
        assert data["user_message"] == "Hello, how are you?"
        assert "assistant_response" in data
        assert "timestamp" in data

    def test_send_message_empty_400(self):
        """Test 400 for empty/whitespace message."""
        with TestClient(app) as client:
            # Create session first
            create_response = client.post(
                "/sessions",
                json={"system_prompt_template": "You are helpful."},
            )
            session_id = create_response.json()["session_id"]

            # Send empty message
            response = client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "   "},
            )

        assert response.status_code == 422 or response.status_code == 400

    def test_send_message_session_not_found_404(self):
        """Test 404 for non-existent session."""
        with TestClient(app) as client:
            response = client.post(
                "/sessions/nonexistent123/messages",
                json={"message": "Hello"},
            )

        assert response.status_code == 404
