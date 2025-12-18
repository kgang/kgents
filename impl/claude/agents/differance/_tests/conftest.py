"""
Differance test fixtures.

Provides buffer isolation for pytest-xdist parallel testing.

Usage:
    The `differance_buffer` fixture is autouse=True, so all tests
    automatically get an isolated buffer. Tests can access it directly:

        def test_my_trace(differance_buffer):
            record_trace_sync(...)
            assert len(differance_buffer) == 1

See: plans/differance-crown-jewel-wiring.md (Phase 6A)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from agents.differance.integration import (
    create_isolated_buffer,
    reset_isolated_buffer,
)

if TYPE_CHECKING:
    from agents.differance.trace import WiringTrace


@pytest.fixture(autouse=True)
def differance_buffer() -> "list[WiringTrace]":
    """
    Create an isolated trace buffer for each test.

    This fixture:
    1. Creates a ContextVar-isolated buffer before each test
    2. Yields the buffer for test inspection
    3. Resets to global buffer after test

    Benefits:
    - pytest-xdist safe (no cross-test pollution)
    - Tests can inspect buffer contents directly
    - No need for manual cleanup
    """
    buffer = create_isolated_buffer()
    yield buffer
    reset_isolated_buffer()
