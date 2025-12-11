"""
A2A (Agent-to-Agent) Protocol Implementation.
Secure communication protocol for multi-agent systems.
"""

import hashlib
import hmac
import json
import time
from typing import Any, Dict

from app.core.config import get_settings
from app.schemas import A2AMessage, A2AResponse


class A2AProtocol:
    """
    Agent-to-Agent protocol implementation for secure multi-agent communication.
    """

    def __init__(self) -> None:
        """Initialize the A2A protocol handler."""
        settings = get_settings()
        self.secret_key = settings.a2a_secret_key.encode()
        self.enabled = settings.a2a_enabled

    def sign_message(self, message: A2AMessage) -> str:
        """
        Sign a message for secure transmission.
        
        Args:
            message: The message to sign
            
        Returns:
            The message signature
        """
        # Create message payload for signing
        payload = {
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "message_type": message.message_type,
            "payload": message.payload,
            "timestamp": message.timestamp or str(int(time.time())),
        }
        
        # Create HMAC signature
        message_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = hmac.new(self.secret_key, message_bytes, hashlib.sha256).hexdigest()
        
        return signature

    def verify_message(self, message: A2AMessage) -> bool:
        """
        Verify a message signature.
        
        Args:
            message: The message to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.enabled:
            return True

        if not message.signature:
            return False

        expected_signature = self.sign_message(message)
        return hmac.compare_digest(message.signature, expected_signature)

    async def send_message(
        self, 
        sender_id: str,
        receiver_id: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> A2AResponse:
        """
        Send a message to another agent.
        
        Args:
            sender_id: ID of the sending agent
            receiver_id: ID of the receiving agent
            message_type: Type of message
            payload: Message payload
            
        Returns:
            Response from the receiving agent
        """
        # Create message
        message = A2AMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload,
            timestamp=str(int(time.time())),
        )
        
        # Sign message
        message.signature = self.sign_message(message)
        
        # In a real implementation, this would send to another service
        # For demo purposes, we'll simulate a response
        return A2AResponse(
            success=True,
            message=f"Message sent from {sender_id} to {receiver_id}",
            data={"message_id": f"{sender_id}-{int(time.time())}"},
        )

    async def receive_message(self, message: A2AMessage) -> A2AResponse:
        """
        Receive and process a message from another agent.
        
        Args:
            message: The incoming message
            
        Returns:
            Response to the sending agent
        """
        # Verify message signature
        if not self.verify_message(message):
            return A2AResponse(
                success=False,
                message="Invalid message signature",
            )
        
        # Process message based on type
        if message.message_type == "query":
            response_data = {"answer": "This is a demo response to your query"}
        elif message.message_type == "action":
            response_data = {"status": "Action received and queued"}
        else:
            response_data = {"status": "Message received"}
        
        return A2AResponse(
            success=True,
            message="Message processed successfully",
            data=response_data,
        )
