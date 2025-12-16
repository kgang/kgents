"""
Base Synergy Handler: Abstract base class for synergy handlers.

Provides common functionality for all synergy handlers:
- Logging
- OTEL tracing
- Result creation helpers
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from ..events import SynergyEvent, SynergyResult


class BaseSynergyHandler(ABC):
    """
    Abstract base class for synergy event handlers.

    Subclasses implement handle() to process specific event types.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"kgents.synergy.{self.name}")

    @property
    @abstractmethod
    def name(self) -> str:
        """Handler name for logging and display."""
        ...

    @abstractmethod
    async def handle(self, event: SynergyEvent) -> SynergyResult:
        """
        Handle a synergy event.

        Args:
            event: The synergy event to handle

        Returns:
            SynergyResult indicating success/failure and any created artifacts
        """
        ...

    # Helper methods for result creation

    def success(
        self,
        message: str,
        artifact_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SynergyResult:
        """Create a successful result."""
        return SynergyResult(
            success=True,
            handler_name=self.name,
            message=message,
            artifact_id=artifact_id,
            metadata=metadata or {},
        )

    def failure(
        self,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> SynergyResult:
        """Create a failure result."""
        return SynergyResult(
            success=False,
            handler_name=self.name,
            message=message,
            metadata=metadata or {},
        )

    def skip(
        self,
        reason: str,
    ) -> SynergyResult:
        """Create a skipped result (success but no action taken)."""
        return SynergyResult(
            success=True,
            handler_name=self.name,
            message=f"Skipped: {reason}",
            metadata={"skipped": True, "reason": reason},
        )


__all__ = ["BaseSynergyHandler"]
