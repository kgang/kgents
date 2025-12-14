"""
Pytest configuration for API tests.

Handles optional FastAPI dependency for integration tests.
"""

from __future__ import annotations

from typing import Generator
from uuid import UUID

import pytest

# Check if FastAPI is available
try:
    import fastapi  # noqa: F401

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# Skip marker for FastAPI-dependent tests
skip_if_no_fastapi = pytest.mark.skipif(
    not HAS_FASTAPI,
    reason="FastAPI not installed (optional dependency)",
)


@pytest.fixture(autouse=True)
def restore_dev_keys() -> Generator[None, None, None]:
    """Restore default dev keys before and after each test."""
    from protocols.api.auth import ApiKeyData, clear_api_keys, register_api_key

    def _register_dev_keys() -> None:
        """Register the default dev keys."""
        dev_keys = [
            ApiKeyData(
                key="kg_dev_alice",
                user_id="user_alice",
                tier="FREE",
                rate_limit=100,
                monthly_token_limit=10000,
                tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
                scopes=("read",),
            ),
            ApiKeyData(
                key="kg_dev_bob",
                user_id="user_bob",
                tier="PRO",
                rate_limit=1000,
                monthly_token_limit=100000,
                tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
                scopes=("read", "write"),
            ),
            ApiKeyData(
                key="kg_dev_carol",
                user_id="user_carol",
                tier="ENTERPRISE",
                rate_limit=10000,
                monthly_token_limit=0,
                tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
                scopes=("read", "write", "admin"),
            ),
        ]
        for key_data in dev_keys:
            register_api_key(key_data)

    # Setup: ensure dev keys are available
    _register_dev_keys()
    yield
    # Teardown: clear and restore dev keys
    clear_api_keys()
    _register_dev_keys()
