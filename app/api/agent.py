"""
Agent endpoints.
"""

from fastapi import APIRouter, HTTPException, status

from app.agents import DemoAgent
from app.schemas import MessageInput, MessageOutput

router = APIRouter()

# Initialize agent (in production, consider dependency injection or singleton pattern)
demo_agent = DemoAgent()


@router.post(
    "/chat",
    response_model=MessageOutput,
    status_code=status.HTTP_200_OK,
    summary="Chat with agent",
    description="Send a message to the demo agent and get a response",
)
async def chat_with_agent(message_input: MessageInput) -> MessageOutput:
    """
    Chat with the demo agent.
    
    This endpoint demonstrates the basic agent workflow using LangGraph.
    """
    try:
        result = await demo_agent.process(
            message=message_input.message,
            session_id=message_input.session_id,
        )
        
        return MessageOutput(
            response=result["response"],
            session_id=result["session_id"],
            metadata=result.get("metadata"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}",
        )


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Get agent status",
    description="Get the current status of the agent",
)
async def get_agent_status() -> dict:
    """Get agent status."""
    return {
        "status": "running",
        "agent_type": "DemoAgent",
        "capabilities": ["chat", "query_processing"],
    }
