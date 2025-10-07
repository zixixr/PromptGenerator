"""Integration test: Sliding window (10-round context)."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_sliding_window_context(client: AsyncClient):
    """Test that only last 10 rounds are sent to Doubao API."""
    # Create session
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "You are a helpful assistant."}
    )
    session_id = create_response.json()["session_id"]

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        mock_send.return_value = "Response"

        # Send 12 messages
        for i in range(12):
            await client.post(
                f"/sessions/{session_id}/messages",
                json={"message": f"Message number {i+1}"}
            )

        # On the 13th message, check the context sent to Doubao
        mock_send.return_value = "Response to message 13"

        # Mock to capture the context
        def capture_context(system_prompt, context, user_message, timeout=6):
            # Context should only include last 10 rounds (rounds 3-12)
            # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            # So 10 rounds = 20 messages (10 user + 10 assistant)
            assert len(context) <= 20, f"Context has {len(context)} messages, expected <= 20"

            # Verify oldest rounds (1-2) are excluded
            # Check that "Message number 1" and "Message number 2" are not in context
            context_str = str(context)
            assert "Message number 1" not in context_str
            assert "Message number 2" not in context_str

            # Verify recent rounds (3-12) are included
            assert "Message number 3" in context_str
            assert "Message number 12" in context_str

            return "Response to message 13"

        mock_send.side_effect = capture_context

        # Send 13th message
        response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "Message number 13"}
        )
        assert response.status_code == 200

    # Cleanup
    await client.delete(f"/sessions/{session_id}")


@pytest.mark.asyncio
async def test_sliding_window_with_fewer_than_10_rounds(client: AsyncClient):
    """Test that all rounds are included when total < 10."""
    # Create session
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "You are a helpful assistant."}
    )
    session_id = create_response.json()["session_id"]

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        # Send 5 messages
        mock_send.return_value = "Response"
        for i in range(5):
            await client.post(
                f"/sessions/{session_id}/messages",
                json={"message": f"Message {i+1}"}
            )

        # On 6th message, verify all 5 previous rounds are in context
        def capture_context(system_prompt, context, user_message, timeout=6):
            # With 5 rounds, context should have 10 messages (5 user + 5 assistant)
            assert len(context) == 10
            return "Response 6"

        mock_send.side_effect = capture_context

        response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "Message 6"}
        )
        assert response.status_code == 200

    # Cleanup
    await client.delete(f"/sessions/{session_id}")


@pytest.mark.asyncio
async def test_sliding_window_exactly_10_rounds(client: AsyncClient):
    """Test edge case: exactly 10 rounds."""
    # Create session
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "Test"}
    )
    session_id = create_response.json()["session_id"]

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        mock_send.return_value = "Response"

        # Send exactly 10 messages
        for i in range(10):
            await client.post(
                f"/sessions/{session_id}/messages",
                json={"message": f"Message {i+1}"}
            )

        # On 11th message, verify only last 10 rounds in context
        def capture_context(system_prompt, context, user_message, timeout=6):
            # Should have exactly 20 messages (10 rounds)
            assert len(context) == 20
            return "Response 11"

        mock_send.side_effect = capture_context

        response = await client.post(
            f"/sessions/{session_id}/messages",
            json={"message": "Message 11"}
        )
        assert response.status_code == 200

    # Cleanup
    await client.delete(f"/sessions/{session_id}")
