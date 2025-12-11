"""
Pydantic schemas for request/response models.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    app_name: str


class MessageInput(BaseModel):
    """Input message for agent."""

    message: str = Field(..., description="The user message to process")
    session_id: Optional[str] = Field(default=None, description="Optional session ID for conversation context")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class MessageOutput(BaseModel):
    """Output message from agent."""

    response: str = Field(..., description="The agent's response")
    session_id: str = Field(..., description="Session ID for this conversation")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class AgentState(BaseModel):
    """Agent state information."""

    session_id: str
    messages: List[Dict[str, str]]
    current_step: int = 0


class A2AMessage(BaseModel):
    """Agent-to-Agent protocol message."""

    sender_id: str = Field(..., description="ID of the sending agent")
    receiver_id: str = Field(..., description="ID of the receiving agent")
    message_type: str = Field(..., description="Type of message (query, response, action, etc.)")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")
    signature: Optional[str] = Field(default=None, description="Message signature for verification")


class A2AResponse(BaseModel):
    """Response for A2A communication."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class CopilotChatMessage(BaseModel):
    """CopilotKit chat message format."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(default=None, description="Optional name for the message sender")


class CopilotChatRequest(BaseModel):
    """CopilotKit chat request."""

    messages: List[CopilotChatMessage] = Field(..., description="Conversation messages")
    model: Optional[str] = Field(default="gpt-4", description="Model to use")
    stream: bool = Field(default=False, description="Whether to stream the response")


class CopilotChatResponse(BaseModel):
    """CopilotKit chat response."""

    message: CopilotChatMessage
    finish_reason: Optional[str] = None
