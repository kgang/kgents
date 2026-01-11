"""
Pilots Service: Registry and metadata for tangible endeavor pilots.

This module provides:
- PilotMetadata: Structured pilot information
- PilotRegistry: Discovery and introspection of pilots

Each pilot follows the Mark -> Trace -> Crystal pipeline and is defined
by a PROTO_SPEC.md file that acts as a BUILD order.

AGENTESE: self.tangibility.pilots

Example:
    from services.pilots import PilotRegistry

    registry = PilotRegistry()
    pilots = await registry.list_pilots(tier="core")
    spec = await registry.get_pilot_spec("trail-to-crystal-daily-lab")

See: pilots/*/PROTO_SPEC.md
"""

from .registry import (
    PilotMetadata,
    PilotRegistry,
    PilotStatus,
    PilotTier,
    get_pilot_registry,
)

__all__ = [
    "PilotMetadata",
    "PilotRegistry",
    "PilotTier",
    "PilotStatus",
    "get_pilot_registry",
]
