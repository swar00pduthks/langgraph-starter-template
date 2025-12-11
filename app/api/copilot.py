"""
CopilotKit integration endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.schemas import CopilotChatRequest, CopilotChatResponse
from app.services import CopilotService

router = APIRouter()

# Initialize service
copilot_service = CopilotService()


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
    status_code=status.HTTP_200_OK,
    summary="CopilotKit chat",
    description="Chat endpoint compatible with CopilotKit",
)
async def copilot_chat(request: CopilotChatRequest) -> CopilotChatResponse:
    """
    CopilotKit compatible chat endpoint.
    
    This endpoint provides AGUI (Agent Graphical User Interface) functionality.
    """
    try:
        response = await copilot_service.chat(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}",
        )


@router.post(
    "/chat/stream",
    summary="CopilotKit streaming chat",
    description="Streaming chat endpoint compatible with CopilotKit",
)
async def copilot_chat_stream(request: CopilotChatRequest):
    """
    CopilotKit compatible streaming chat endpoint.
    
    Streams responses for real-time chat experience.
    """
    try:
        async def event_generator():
            async for chunk in copilot_service.chat_stream(request):
                yield {
                    "event": "message",
                    "data": chunk,
                }
            yield {
                "event": "done",
                "data": "[DONE]",
            }
        
        return EventSourceResponse(event_generator())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming chat: {str(e)}",
        )
