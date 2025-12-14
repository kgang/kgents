"""
Pytest configuration for API tests.

Handles optional FastAPI dependency for integration tests.
"""

from __future__ import annotations

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
