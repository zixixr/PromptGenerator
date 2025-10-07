"""Integration test: Concurrent message queuing."""
import pytest
from httpx import AsyncClient
import asyncio
from unittest.mock import patch


@pytest.mark.asyncio
async def test_concurrent_message_queuing(client: AsyncClient):
    """Test sending 3 concurrent messages using asyncio.gather()."""
    # Create session
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "You are a helpful assistant."}
    )
    session_id = create_response.json()["session_id"]

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        # Mock Doubao responses
        call_count = 0

        def mock_response(system_prompt, context, user_message, timeout=6):
            nonlocal call_count
            call_count += 1
            # Add small delay to simulate API call
            import time
            time.sleep(0.1)
            return f"Response {call_count}"

        mock_send.side_effect = mock_response

        # Send 3 concurrent messages
        responses = await asyncio.gather(
            client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "First concurrent message"}
            ),
            client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "Second concurrent message"}
            ),
            client.post(
                f"/sessions/{session_id}/messages",
                json={"message": "Third concurrent message"}
            )
        )

        # Assert all 3 messages processed
        assert all(r.status_code == 200 for r in responses)

        # Extract round numbers
        round_numbers = [r.json()["round_number"] for r in responses]

        # Assert round numbers are 1, 2, 3 (FIFO order maintained)
        assert sorted(round_numbers) == [1, 2, 3]

        # Assert no duplicate round numbers (no race conditions)
        assert len(set(round_numbers)) == 3

    # Verify history has all 3 messages
    history = await client.get(f"/sessions/{session_id}/history")
    assert len(history.json()["rounds"]) == 3

    # Cleanup
    await client.delete(f"/sessions/{session_id}")


@pytest.mark.asyncio
async def test_concurrent_messages_maintain_order(client: AsyncClient):
    """Test that concurrent messages are processed in order."""
    # Create session
    create_response = await client.post(
        "/sessions",
        json={"system_prompt_template": "Test"}
    )
    session_id = create_response.json()["session_id"]

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        mock_send.return_value = "Response"

        # Send 5 concurrent messages
        messages = [f"Message {i}" for i in range(1, 6)]
        tasks = [
            client.post(
                f"/sessions/{session_id}/messages",
                json={"message": msg}
            )
            for msg in messages
        ]

        responses = await asyncio.gather(*tasks)

        # Get history
        history = await client.get(f"/sessions/{session_id}/history")
        rounds = history.json()["rounds"]

        # Verify 5 rounds exist
        assert len(rounds) == 5

        # Verify round numbers are sequential
        for i, round_data in enumerate(rounds, 1):
            assert round_data["round_number"] == i

    # Cleanup
    await client.delete(f"/sessions/{session_id}")


@pytest.mark.asyncio
async def test_concurrent_messages_to_different_sessions(client: AsyncClient):
    """Test concurrent messages to different sessions process in parallel."""
    # Create 3 sessions
    sessions = []
    for i in range(3):
        response = await client.post(
            "/sessions",
            json={"system_prompt_template": f"Session {i}"}
        )
        sessions.append(response.json()["session_id"])

    with patch("src.services.doubao_client.DoubaClient.send_message") as mock_send:
        mock_send.return_value = "Response"

        # Send message to each session concurrently
        tasks = [
            client.post(
                f"/sessions/{sid}/messages",
                json={"message": f"Message to session {i}"}
            )
            for i, sid in enumerate(sessions)
        ]

        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # Each should be round 1 (different sessions)
        assert all(r.json()["round_number"] == 1 for r in responses)

    # Cleanup
    for sid in sessions:
        await client.delete(f"/sessions/{sid}")
