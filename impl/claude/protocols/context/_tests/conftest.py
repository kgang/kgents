"""
Test configuration for Context Perception tests.

Note: pytest-asyncio is configured via asyncio_mode="auto" in pyproject.toml.
"""

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"
