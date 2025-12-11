"""
CopilotKit integration service.
Provides chat interface compatible with CopilotKit and AGUI.
"""

from typing import Any, AsyncGenerator, Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.schemas import CopilotChatMessage, CopilotChatRequest, CopilotChatResponse


class CopilotService:
    """
    Service for CopilotKit integration providing AGUI chatbot interface.
    """

    def __init__(self) -> None:
        """Initialize the CopilotKit service."""
        settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=settings.openai_api_key,
            temperature=0.7,
        )

    def _convert_messages(self, messages: List[CopilotChatMessage]) -> List[Any]:
        """Convert CopilotKit messages to LangChain format."""
        lc_messages = []
        for msg in messages:
            if msg.role == "system":
                lc_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
            else:
                lc_messages.append(HumanMessage(content=msg.content))
        return lc_messages

    async def chat(self, request: CopilotChatRequest) -> CopilotChatResponse:
        """
        Process a chat request from CopilotKit.
        
        Args:
            request: The chat request
            
        Returns:
            Chat response
        """
        # Convert messages
        lc_messages = self._convert_messages(request.messages)
        
        # Get response from LLM
        response = await self.llm.ainvoke(lc_messages)
        
        # Create response message
        response_message = CopilotChatMessage(
            role="assistant",
            content=response.content,
        )
        
        return CopilotChatResponse(
            message=response_message,
            finish_reason="stop",
        )

    async def chat_stream(
        self, request: CopilotChatRequest
    ) -> AsyncGenerator[str, None]:
        """
        Stream a chat response from CopilotKit.
        
        Args:
            request: The chat request
            
        Yields:
            Chunks of the response
        """
        # Convert messages
        lc_messages = self._convert_messages(request.messages)
        
        # Stream response from LLM
        async for chunk in self.llm.astream(lc_messages):
            if chunk.content:
                yield chunk.content
