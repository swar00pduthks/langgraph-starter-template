"""
FastAPI application setup and configuration.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import agent_router, copilot_router, health_router, a2a_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()
    
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize monitoring if enabled
    if settings.enable_monitoring and settings.applicationinsights_connection_string:
        print("Monitoring enabled")
    
    yield
    
    # Shutdown
    print("Shutting down application")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-ready LangGraph starter template with FastAPI, CopilotKit, and A2A protocol",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(
        agent_router, 
        prefix=f"{settings.api_prefix}/agent", 
        tags=["Agent"]
    )
    app.include_router(
        copilot_router, 
        prefix=f"{settings.api_prefix}/copilot", 
        tags=["CopilotKit"]
    )
    app.include_router(
        a2a_router, 
        prefix=f"{settings.api_prefix}/a2a", 
        tags=["A2A Protocol"]
    )

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc) if settings.debug else "An error occurred"
            }
        )

    return app


app = create_application()
