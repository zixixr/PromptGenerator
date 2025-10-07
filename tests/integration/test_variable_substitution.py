"""Integration test: Mustache variable substitution."""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_normal_substitution(client: AsyncClient):
    """Test normal variable substitution: {{role}} → 'helpful'."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "You are a {{role}} assistant.",
            "variables": {"role": "helpful"}
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["resolved_system_prompt"] == "You are a helpful assistant."

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_missing_variable(client: AsyncClient):
    """Test missing variable: {{expertise}} → '' (empty string)."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "You are a {{role}} assistant. Your expertise is {{expertise}}.",
            "variables": {"role": "helpful"}
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    # Missing variable should be replaced with empty string
    assert data["resolved_system_prompt"] == "You are a helpful assistant. Your expertise is ."

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_multiple_variables(client: AsyncClient):
    """Test multiple variables: {{role}} + {{domain}} + {{tone}}."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "You are a {{role}} assistant specializing in {{domain}}. Your tone is {{tone}}.",
            "variables": {
                "role": "friendly",
                "domain": "Python programming",
                "tone": "professional"
            }
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    expected = "You are a friendly assistant specializing in Python programming. Your tone is professional."
    assert data["resolved_system_prompt"] == expected

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_no_variables_plain_text(client: AsyncClient):
    """Test no variables (plain text prompt)."""
    plain_text = "You are a helpful assistant with no variables."
    response = await client.post(
        "/sessions",
        json={"system_prompt_template": plain_text}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["resolved_system_prompt"] == plain_text

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_special_characters_in_template(client: AsyncClient):
    """Test template with special characters and variables."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "你是一个{{role}}助手。Support UTF-8: {{lang}}!",
            "variables": {
                "role": "有帮助的",
                "lang": "中文"
            }
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["resolved_system_prompt"] == "你是一个有帮助的助手。Support UTF-8: 中文!"

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_extra_variables_ignored(client: AsyncClient):
    """Test that extra variables (not in template) are ignored."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "You are a {{role}} assistant.",
            "variables": {
                "role": "helpful",
                "extra_var": "ignored",
                "another_extra": "also ignored"
            }
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    # Extra variables should not affect the output
    assert data["resolved_system_prompt"] == "You are a helpful assistant."

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")


@pytest.mark.asyncio
async def test_same_variable_multiple_times(client: AsyncClient):
    """Test same variable appearing multiple times in template."""
    response = await client.post(
        "/sessions",
        json={
            "system_prompt_template": "{{name}}, you are {{name}}. Remember: {{name}}!",
            "variables": {"name": "Claude"}
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["resolved_system_prompt"] == "Claude, you are Claude. Remember: Claude!"

    # Cleanup
    await client.delete(f"/sessions/{data['session_id']}")
