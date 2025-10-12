"""Integration test: Full session workflow."""
import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch
import os


@pytest.mark.asyncio
async def test_session_workflow(client: AsyncClient):
    """Test: Create session → Send 2 messages → Get history → Delete session."""
    # Step 1: Create session
    create_response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "You are a {{role}} assistant",
            "variables": {"role": "helpful"}
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    session_id = create_response.json()["session_id"]
    assert create_response.json()["resolved_system_prompt"] == "You are a helpful assistant"

    # Step 2: Send first message
    with patch("src.services.doubao_client.DoubaoClient.send_message") as mock_send:
        mock_send.return_value = "Response to first message"

        msg1_response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "What is Python?"}
        )
        assert msg1_response.status_code == status.HTTP_200_OK
        msg1_data = msg1_response.json()
        assert msg1_data["session_id"] == session_id
        assert msg1_data["round_number"] == 1
        assert msg1_data["user_message"] == "What is Python?"

        # Step 3: Send second message
        mock_send.return_value = "Response to second message"

        msg2_response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "Can you explain more?"}
        )
        assert msg2_response.status_code == status.HTTP_200_OK
        msg2_data = msg2_response.json()
        assert msg2_data["session_id"] == session_id
        assert msg2_data["round_number"] == 2

    # Step 4: Get history
    history_response = await client.get(f"/sessions/{session_id}/history")
    assert history_response.status_code == status.HTTP_200_OK
    history_data = history_response.json()

    # Assert session_id consistency
    assert history_data["session_id"] == session_id

    # Assert round numbers increment correctly
    assert len(history_data["rounds"]) == 2
    assert history_data["rounds"][0]["round_number"] == 1
    assert history_data["rounds"][1]["round_number"] == 2

    # Assert last_activity updated after each message
    assert history_data["last_activity"] > history_data["created_at"]

    # Validate JSON history file created (if file storage is implemented)
    conversations_dir = os.path.join(os.getcwd(), "conversations")
    if os.path.exists(conversations_dir):
        json_files = [f for f in os.listdir(conversations_dir) if session_id in f]
        assert len(json_files) >= 1

    # Step 5: Delete session
    delete_response = await client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify session is deleted
    get_after_delete = await client.get(f"/sessions/{session_id}/history")
    assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_workflow_with_no_variables(client: AsyncClient):
    """Test workflow with plain text system prompt (no variables)."""
    # Create session without variables
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "You are a helpful assistant."}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    session_id = create_response.json()["session_id"]

    # Send message
    with patch("src.services.doubao_client.DoubaoClient.send_message") as mock_send:
        mock_send.return_value = "Response"

        msg_response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "Hello"}
        )
        assert msg_response.status_code == status.HTTP_200_OK

    # Cleanup
    await client.delete(f"/sessions/{session_id}")
