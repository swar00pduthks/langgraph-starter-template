"""Tests for A2A protocol endpoints."""

from fastapi import status


def test_a2a_status(client):
    """Test A2A status endpoint."""
    response = client.get("/api/v1/a2a/status")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "enabled" in data
    assert "protocol_version" in data


def test_send_a2a_message(client):
    """Test sending A2A message."""
    message = {
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "message_type": "query",
        "payload": {"question": "What is the weather?"},
    }
    
    response = client.post("/api/v1/a2a/send", json=message)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True


def test_receive_a2a_message(client):
    """Test receiving A2A message."""
    message = {
        "sender_id": "agent-1",
        "receiver_id": "agent-2",
        "message_type": "query",
        "payload": {"question": "What is the weather?"},
        "timestamp": "1234567890",
        "signature": "test-signature",
    }
    
    response = client.post("/api/v1/a2a/receive", json=message)
    # Will fail signature validation but endpoint should work
    assert response.status_code == status.HTTP_200_OK
