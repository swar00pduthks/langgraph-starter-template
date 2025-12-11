"""
A2A (Agent-to-Agent) Protocol endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas import A2AMessage, A2AResponse
from app.services import A2AProtocol

router = APIRouter()

# Initialize A2A protocol
a2a_protocol = A2AProtocol()


@router.post(
    "/send",
    response_model=A2AResponse,
    status_code=status.HTTP_200_OK,
    summary="Send A2A message",
    description="Send a message using the Agent-to-Agent protocol",
)
async def send_a2a_message(message: A2AMessage) -> A2AResponse:
    """
    Send a message to another agent using A2A protocol.
    
    The message will be signed for secure transmission.
    """
    try:
        response = await a2a_protocol.send_message(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            message_type=message.message_type,
            payload=message.payload,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending A2A message: {str(e)}",
        )


@router.post(
    "/receive",
    response_model=A2AResponse,
    status_code=status.HTTP_200_OK,
    summary="Receive A2A message",
    description="Receive and process a message using the Agent-to-Agent protocol",
)
async def receive_a2a_message(message: A2AMessage) -> A2AResponse:
    """
    Receive and process a message from another agent using A2A protocol.
    
    The message signature will be verified before processing.
    """
    try:
        response = await a2a_protocol.receive_message(message)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error receiving A2A message: {str(e)}",
        )


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Get A2A status",
    description="Get the current status of A2A protocol",
)
async def get_a2a_status() -> dict:
    """Get A2A protocol status."""
    return {
        "enabled": a2a_protocol.enabled,
        "protocol_version": "1.0",
        "supported_message_types": ["query", "response", "action"],
    }
