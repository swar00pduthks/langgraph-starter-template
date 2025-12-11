"""API module initialization."""

from app.api.a2a import router as a2a_router
from app.api.agent import router as agent_router
from app.api.copilot import router as copilot_router
from app.api.health import router as health_router

__all__ = ["health_router", "agent_router", "copilot_router", "a2a_router"]
