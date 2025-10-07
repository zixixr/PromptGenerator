import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from src.services.doubao_client import DoubaoClient


@pytest.fixture
def mock_doubao_client():
    """Mock Doubao client for testing."""
    client = AsyncMock(spec=DoubaoClient)
    client.send_message = AsyncMock(
        return_value="This is a mocked response from Doubao API."
    )
    return client


@pytest.fixture
def test_env():
    """Set test environment variables."""
    os.environ["DOUBAO_API_KEY"] = "test_api_key_123"
    os.environ["MAX_SESSIONS"] = "50"
    os.environ["CONVERSATIONS_DIR"] = "./test_conversations"
    yield
    # Cleanup
    if "DOUBAO_API_KEY" in os.environ:
        del os.environ["DOUBAO_API_KEY"]
