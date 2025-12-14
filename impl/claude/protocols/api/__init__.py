"""
Soul API Service - K-gent Soul as a Service.

FastAPI-based REST API exposing K-gent Soul capabilities:
- /v1/soul/governance - Semantic gatekeeper for operations
- /v1/soul/dialogue - Interactive dialogue with K-gent
- /health - Service health check

Architecture:
    - API key authentication
    - Usage metering middleware
    - OpenAPI documentation
    - Graceful FastAPI dependency handling
"""

from __future__ import annotations

__all__ = [
    "create_app",
    "ApiKeyData",
    "GovernanceRequest",
    "GovernanceResponse",
    "DialogueRequest",
    "DialogueResponse",
]

# Graceful FastAPI import
try:
    from .app import create_app
    from .auth import ApiKeyData
    from .models import (
        DialogueRequest,
        DialogueResponse,
        GovernanceRequest,
        GovernanceResponse,
    )

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

    def create_app() -> None:  # type: ignore[misc]
        """FastAPI is not installed."""
        raise ImportError(
            "FastAPI is not installed. Install with: pip install fastapi uvicorn"
        )

    class ApiKeyData:  # type: ignore[no-redef]
        """Stub for when FastAPI is not installed."""

        pass

    class GovernanceRequest:  # type: ignore[no-redef]
        """Stub for when FastAPI is not installed."""

        pass

    class GovernanceResponse:  # type: ignore[no-redef]
        """Stub for when FastAPI is not installed."""

        pass

    class DialogueRequest:  # type: ignore[no-redef]
        """Stub for when FastAPI is not installed."""

        pass

    class DialogueResponse:  # type: ignore[no-redef]
        """Stub for when FastAPI is not installed."""

        pass
