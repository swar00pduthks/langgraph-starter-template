"""
Health check endpoints.
"""

from fastapi import APIRouter, status

from app.core.config import get_settings
from app.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the application is running",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        app_name=settings.app_name,
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the application is ready to serve requests",
)
async def readiness_check() -> dict:
    """Readiness check endpoint."""
    return {"status": "ready"}


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Check if the application is alive",
)
async def liveness_check() -> dict:
    """Liveness check endpoint."""
    return {"status": "alive"}
