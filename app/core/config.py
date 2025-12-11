"""
Core configuration module for the application.
Manages environment variables and application settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "LangGraph Starter Template"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    
    # API
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    
    # OpenAI / LangChain
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    langchain_api_key: Optional[str] = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_tracing_v2: bool = Field(default=False, validation_alias="LANGCHAIN_TRACING_V2")
    
    # Azure
    azure_key_vault_name: Optional[str] = Field(default=None, validation_alias="AZURE_KEY_VAULT_NAME")
    azure_tenant_id: Optional[str] = Field(default=None, validation_alias="AZURE_TENANT_ID")
    azure_client_id: Optional[str] = Field(default=None, validation_alias="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(default=None, validation_alias="AZURE_CLIENT_SECRET")
    
    # Monitoring
    enable_monitoring: bool = Field(default=False, validation_alias="ENABLE_MONITORING")
    applicationinsights_connection_string: Optional[str] = Field(
        default=None, validation_alias="APPLICATIONINSIGHTS_CONNECTION_STRING"
    )
    
    # A2A Protocol
    a2a_enabled: bool = Field(default=True, validation_alias="A2A_ENABLED")
    a2a_secret_key: str = Field(default="change-me-in-production", validation_alias="A2A_SECRET_KEY")
    
    # MCP Integration
    mcp_enabled: bool = Field(default=False, validation_alias="MCP_ENABLED")
    mcp_endpoint: Optional[str] = Field(default=None, validation_alias="MCP_ENDPOINT")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
