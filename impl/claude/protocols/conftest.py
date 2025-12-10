"""
Protocol-level pytest configuration.

Philosophy: Protocols are the boundaries where agents meet the world.

This conftest provides:
- Protocol test fixtures
- Wire protocol helpers
"""

import pytest
from typing import Any


# =============================================================================
# Protocol Fixtures
# =============================================================================


@pytest.fixture
def mock_wire():
    """Mock wire for protocol testing."""
    from dataclasses import dataclass, field

    @dataclass
    class MockWire:
        """Mock wire that captures emissions."""

        emissions: list[Any] = field(default_factory=list)

        async def emit(self, message: Any) -> None:
            self.emissions.append(message)

        def clear(self) -> None:
            self.emissions.clear()

    return MockWire()
