"""
Phase 6: Portal Token → Derivation Bridge (Bidirectional).

This module implements bidirectional sync between portal tokens and derivation:
1. Portal → Derivation: Expansion events contribute stigmergic evidence
2. Derivation → Portal: Confidence gates portal trust level

The insight: portals are *used* by agents. Usage patterns (expansions, depth,
frequency) signal that an agent is useful. This is stigmergic evidence.

Laws:
    6.2a (Portal Usage Accumulates): Expansion events increment usage count
    6.2b (Trust Bounded by Confidence): portal_trust(A) <= derivation_confidence(A)

See: spec/protocols/derivation-framework.md §6.2
See: spec/protocols/portal-token.md

Teaching:
    gotcha: The 0.9 factor in derivation_to_portal_trust ensures portals are
            slightly more conservative than raw confidence—trust must be earned.
            (Evidence: test_portal_bridge.py::test_trust_conservative)

    gotcha: Path extraction uses simple heuristics. "world.brain" → "Brain".
            Complex paths may need custom mapping.
            (Evidence: test_portal_bridge.py::test_path_extraction)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .registry import DerivationRegistry


# =============================================================================
# Path Utilities
# =============================================================================


def path_to_agent_name(path: str) -> str | None:
    """
    Extract agent name from AGENTESE path.

    Examples:
        "world.brain" → "Brain"
        "world.brain.persistence" → "Brain"
        "self.witness" → "Witness"
        "concept.agent.Flux" → "Flux"

    Returns None if path doesn't map to an agent.

    Teaching:
        gotcha: This uses simple heuristics. For complex path structures,
                you may need to extend the mapping logic.
    """
    if not path:
        return None

    parts = path.split(".")

    # Handle concept.agent.* paths (direct agent reference)
    if len(parts) >= 3 and parts[0] == "concept" and parts[1] == "agent":
        return parts[2]

    # Handle world.* and self.* paths
    if len(parts) >= 2 and parts[0] in ("world", "self"):
        # Capitalize the second part as agent name
        # e.g., "world.brain" → "Brain", "self.witness" → "Witness"
        return parts[1].capitalize()

    return None


def agent_name_to_paths(agent_name: str) -> list[str]:
    """
    Generate possible AGENTESE paths for an agent name.

    Inverse of path_to_agent_name for registration/lookup.

    Examples:
        "Brain" → ["world.brain", "self.brain", "concept.agent.Brain"]
    """
    lower = agent_name.lower()
    return [
        f"world.{lower}",
        f"self.{lower}",
        f"concept.agent.{agent_name}",
    ]


# =============================================================================
# Portal Open Signal (from portal-token.md)
# =============================================================================


@dataclass(frozen=True)
class PortalOpenSignal:
    """
    Signal emitted when a portal expands.

    Captures:
    1. Which file(s) are now "open"
    2. The edge type that led here
    3. The nesting depth
    4. The parent context

    This signal is the input for Portal → Derivation evidence flow.
    """

    paths_opened: tuple[str, ...]
    edge_type: str
    parent_path: str
    depth: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_expansion(
        cls,
        portal_path: str,
        files_opened: list[str] | tuple[str, ...],
        edge_type: str = "portal",
        depth: int = 0,
    ) -> "PortalOpenSignal":
        """Create signal from portal expansion event."""
        return cls(
            paths_opened=tuple(files_opened) if isinstance(files_opened, list) else files_opened,
            edge_type=edge_type,
            parent_path=portal_path,
            depth=depth,
        )


# =============================================================================
# Bidirectional Sync
# =============================================================================


@dataclass(frozen=True)
class PortalDerivationSync:
    """
    Bidirectional sync between portal tokens and derivation confidence.

    Direction 1: Portal → Derivation
        Expansion events contribute stigmergic evidence.
        Each expansion increments usage count.

    Direction 2: Derivation → Portal
        Confidence gates portal trust level.
        Trust = min(total_confidence, tier.ceiling * 0.9)
    """

    @staticmethod
    def portal_expansion_to_derivation(
        signal: PortalOpenSignal,
        registry: "DerivationRegistry",
    ) -> list[str]:
        """
        Portal expansion events contribute stigmergic evidence.

        Law 6.2a: Expansion events increment usage count.

        Args:
            signal: The portal open signal
            registry: The derivation registry

        Returns:
            List of agent names that were updated
        """
        updated_agents: list[str] = []

        for path in signal.paths_opened:
            agent_name = path_to_agent_name(path)
            if agent_name and registry.exists(agent_name):
                registry.increment_usage(agent_name)
                updated_agents.append(agent_name)

        return updated_agents

    @staticmethod
    async def portal_expansion_to_derivation_async(
        signal: PortalOpenSignal,
        registry: "DerivationRegistry",
    ) -> list[str]:
        """Async version for event-driven contexts."""
        return PortalDerivationSync.portal_expansion_to_derivation(signal, registry)

    @staticmethod
    def derivation_to_portal_trust(
        agent_name: str,
        registry: "DerivationRegistry",
    ) -> float:
        """
        Compute portal trust from derivation confidence.

        Law 6.2b: Portal trust is bounded by derivation confidence.

        Trust = min(total_confidence, tier.ceiling * 0.9)

        The 0.9 factor ensures portals are slightly more conservative
        than raw confidence—trust must be earned through use.

        Args:
            agent_name: The agent to compute trust for
            registry: The derivation registry

        Returns:
            Trust level (0.0-1.0), 0.3 for unknown agents
        """
        if not registry.exists(agent_name):
            return 0.3  # Unknown agents get low trust

        derivation = registry.get(agent_name)
        if derivation is None:
            return 0.3

        # Trust is bounded by confidence AND tier ceiling
        return min(
            derivation.total_confidence,
            derivation.tier.ceiling * 0.9,
        )

    @staticmethod
    def bulk_compute_trust(
        agent_names: list[str],
        registry: "DerivationRegistry",
    ) -> dict[str, float]:
        """
        Compute trust for multiple agents efficiently.

        Returns:
            Dict mapping agent_name → trust level
        """
        return {
            name: PortalDerivationSync.derivation_to_portal_trust(name, registry)
            for name in agent_names
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def portal_expansion_to_derivation(
    signal: PortalOpenSignal,
    registry: "DerivationRegistry",
) -> list[str]:
    """
    Process portal expansion event, updating derivation stigmergic evidence.

    Convenience wrapper around PortalDerivationSync.portal_expansion_to_derivation().
    """
    return PortalDerivationSync.portal_expansion_to_derivation(signal, registry)


def derivation_to_portal_trust(
    agent_name: str,
    registry: "DerivationRegistry",
) -> float:
    """
    Compute portal trust from derivation confidence.

    Convenience wrapper around PortalDerivationSync.derivation_to_portal_trust().
    """
    return PortalDerivationSync.derivation_to_portal_trust(agent_name, registry)


def sync_portal_expansion(
    portal_path: str,
    files_opened: list[str],
    registry: "DerivationRegistry",
    edge_type: str = "portal",
    depth: int = 0,
) -> list[str]:
    """
    One-shot convenience function for portal expansion sync.

    Creates signal and applies to registry in one call.

    Args:
        portal_path: The portal that was expanded
        files_opened: Paths of files opened by expansion
        registry: The derivation registry
        edge_type: Type of edge followed
        depth: Expansion depth

    Returns:
        List of updated agent names
    """
    signal = PortalOpenSignal.from_expansion(
        portal_path=portal_path,
        files_opened=files_opened,
        edge_type=edge_type,
        depth=depth,
    )
    return portal_expansion_to_derivation(signal, registry)


def get_trust_for_path(
    path: str,
    registry: "DerivationRegistry",
) -> float:
    """
    Get portal trust for an AGENTESE path.

    Extracts agent name from path, then computes trust.

    Args:
        path: AGENTESE path (e.g., "world.brain")
        registry: The derivation registry

    Returns:
        Trust level (0.0-1.0), 0.3 if agent not found
    """
    agent_name = path_to_agent_name(path)
    if agent_name is None:
        return 0.3
    return derivation_to_portal_trust(agent_name, registry)


__all__ = [
    # Path utilities
    "path_to_agent_name",
    "agent_name_to_paths",
    # Signal type
    "PortalOpenSignal",
    # Main sync class
    "PortalDerivationSync",
    # Convenience functions
    "portal_expansion_to_derivation",
    "derivation_to_portal_trust",
    "sync_portal_expansion",
    "get_trust_for_path",
]
