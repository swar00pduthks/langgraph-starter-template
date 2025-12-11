"""
LangGraph Agent implementation.
Demonstrates a simple agent workflow using LangGraph.
"""

import uuid
from typing import Any, Dict, List, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.core.config import get_settings


class AgentState(TypedDict):
    """State for the agent graph."""

    messages: List[Any]
    session_id: str
    current_step: int


class DemoAgent:
    """
    Demo agent that processes user queries using LangGraph.
    This is a simple example demonstrating agent workflow.
    """

    def __init__(self) -> None:
        """Initialize the demo agent."""
        settings = get_settings()
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=settings.openai_api_key,
            temperature=0.7,
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("process", self._process_message)
        workflow.add_node("respond", self._generate_response)

        # Add edges
        workflow.set_entry_point("process")
        workflow.add_edge("process", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile()

    def _process_message(self, state: AgentState) -> AgentState:
        """Process the incoming message."""
        state["current_step"] += 1
        return state

    def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a response using the LLM."""
        messages = state["messages"]
        
        # Convert to LangChain message format
        lc_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=content))
            else:
                lc_messages.append(msg)

        # Get response from LLM
        response = self.llm.invoke(lc_messages)
        
        # Add response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })
        
        return state

    async def process(self, message: str, session_id: str | None = None) -> Dict[str, Any]:
        """
        Process a message through the agent workflow.
        
        Args:
            message: The user message to process
            session_id: Optional session ID for context
            
        Returns:
            Dictionary containing the response and session information
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        initial_state: AgentState = {
            "messages": [{"role": "user", "content": message}],
            "session_id": session_id,
            "current_step": 0,
        }

        # Run the graph
        result = await self.graph.ainvoke(initial_state)

        # Extract the last assistant message
        assistant_messages = [
            msg for msg in result["messages"] 
            if isinstance(msg, dict) and msg.get("role") == "assistant"
        ]
        
        response_text = assistant_messages[-1]["content"] if assistant_messages else "No response generated"

        return {
            "response": response_text,
            "session_id": result["session_id"],
            "metadata": {
                "steps": result["current_step"],
                "message_count": len(result["messages"]),
            },
        }
