"""
Bridge external process events to the Witness system.

This allows non-AGENTESE processes to participate in the unified
observability layer via Witness marks.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from .observer import WireEvent


async def bridge_to_witness(
    events: AsyncIterator[WireEvent],
    witness: Any,  # WitnessPersistence or compatible mark() interface
    walk_id: str | None = None,
) -> None:
    """
    Convert WireEvents to Witness marks.

    Each event becomes a mark in the current walk, providing
    unified traceability for external processes.
    """
    async for event in events:
        await witness.mark(
            action=f"external.{event.stage}",
            reasoning=event.message,
            metadata={
                "level": event.level,
                "source": "w-gent",
                **event.metadata,
            },
        )
