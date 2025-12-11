"""Tests for agent endpoints."""

from unittest.mock import AsyncMock, patch

from fastapi import status


def test_agent_status(client):
    """Test agent status endpoint."""
    response = client.get("/api/v1/agent/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "running"
    assert "agent_type" in data


@patch("app.api.agent.demo_agent")
def test_chat_with_agent(mock_agent, client, mock_openai_api_key):
    """Test chat endpoint with mocked agent."""
    # Mock the agent's process method
    mock_agent.process = AsyncMock(
        return_value={
            "response": "This is a test response",
            "session_id": "test-session-123",
            "metadata": {"steps": 2, "message_count": 2},
        }
    )

    # Make request
    response = client.post(
        "/api/v1/agent/chat",
        json={"message": "Hello, agent!"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "response" in data
    assert "session_id" in data


def test_chat_with_agent_invalid_input(client):
    """Test chat endpoint with invalid input."""
    response = client.post(
        "/api/v1/agent/chat",
        json={},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
