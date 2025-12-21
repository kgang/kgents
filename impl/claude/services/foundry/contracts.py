"""
Foundry Contracts — Request/Response types for the Agent Foundry.

These dataclasses define the typed contracts for AGENTESE node aspects.
Following the Phase 7 Autopoietic Architecture pattern from Brain/Witness.

All contracts are FROZEN dataclasses — immutable after creation. This:
1. Prevents accidental mutation across layer boundaries
2. Enables safe caching (hashable keys)
3. Makes debugging easier (no spooky action at a distance)

AGENTESE: self.foundry.* (forge, inspect, cache, promote, manifest)

Teaching:
    gotcha: All Request/Response types are frozen=True. This is intentional.
            If you need to modify a request, create a new one. Never use
            mutable dataclasses for cross-layer contracts.
            (Evidence: services/foundry/_tests/test_core.py — all tests use frozen contracts)

    gotcha: ForgeResponse includes both `forced` and `reason` fields.
            When `forced=True`, the target was chosen by a safety constraint
            (CHAOTIC → WASM), not user preference. The `reason` explains why.
            (Evidence: services/foundry/_tests/test_core.py::TestForgeBasics::test_forge_chaotic_intent)

    gotcha: InspectResponse distinguishes ephemeral from registered agents
            via `is_ephemeral` flag. Ephemeral agents have cache_metrics,
            registered agents have halo and polynomial.
            (Evidence: services/foundry/_tests/test_core.py::TestInspect::test_inspect_cached_agent)

Example:
    >>> request = ForgeRequest(
    ...     intent="parse JSON data",
    ...     context={"interactive": True},
    ...     entropy_budget=0.8,
    ... )
    >>> # request.intent = "new"  # ERROR: frozen dataclass
    >>> request.to_dict()  # Works for all Response types too
    {'intent': 'parse JSON data', ...}

See: spec/services/foundry.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# =============================================================================
# Forge Contracts
# =============================================================================


@dataclass(frozen=True)
class ForgeRequest:
    """
    Request to forge a new ephemeral agent.

    The Foundry will:
    1. Classify intent (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
    2. Generate source if PROBABILISTIC
    3. Validate stability via Chaosmonger
    4. Select projection target
    5. Compile to artifact
    6. Cache for reuse
    """

    intent: str  # Natural language description of what the agent should do
    context: dict[str, Any] = field(default_factory=dict)  # Context flags
    target_override: str | None = (
        None  # Force specific target (local, cli, docker, k8s, wasm, marimo)
    )
    entropy_budget: float = 1.0  # Computation budget (0.0-1.0)


@dataclass(frozen=True)
class ForgeResponse:
    """
    Response from forge operation.

    Contains the compiled artifact and metadata for inspection/promotion.
    """

    success: bool
    cache_key: str | None  # SHA256 hash for cache lookup
    target: str  # Selected target (local, cli, docker, k8s, wasm, marimo)
    artifact_type: str  # "script" | "dockerfile" | "html" | "manifests" | "agent"
    artifact: str | list[dict[str, Any]] | None  # The compiled output
    reality: str  # DETERMINISTIC | PROBABILISTIC | CHAOTIC
    stability_score: float | None  # 0.0-1.0 if analyzed
    agent_source: str | None  # Generated Python source (if PROBABILISTIC)
    forced: bool = False  # True if target was forced by safety constraint
    reason: str | None = None  # Explanation of target selection
    error: str | None = None  # Error message if success=False

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "success": self.success,
            "cache_key": self.cache_key,
            "target": self.target,
            "artifact_type": self.artifact_type,
            "artifact": self.artifact,
            "reality": self.reality,
            "stability_score": self.stability_score,
            "agent_source": self.agent_source,
            "forced": self.forced,
            "reason": self.reason,
            "error": self.error,
        }


# =============================================================================
# Inspect Contracts
# =============================================================================


@dataclass(frozen=True)
class InspectRequest:
    """Request to inspect a registered or cached agent."""

    agent_name: str  # Name of agent to inspect (or cache_key for ephemeral)
    include_source: bool = False  # Include source code if available


@dataclass(frozen=True)
class InspectResponse:
    """Response from inspect operation."""

    found: bool
    agent_name: str | None
    halo: list[dict[str, Any]] | None  # Capability metadata
    polynomial: dict[str, Any] | None  # State machine definition if exists
    aspects: list[str] | None  # Available aspects
    source: str | None  # Source code if requested and available
    is_ephemeral: bool = False  # True if this is a cached JIT agent
    cache_metrics: dict[str, Any] | None = None  # Invocation counts etc.

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "found": self.found,
            "agent_name": self.agent_name,
            "halo": self.halo,
            "polynomial": self.polynomial,
            "aspects": self.aspects,
            "source": self.source,
            "is_ephemeral": self.is_ephemeral,
            "cache_metrics": self.cache_metrics,
        }


# =============================================================================
# Cache Contracts
# =============================================================================


@dataclass(frozen=True)
class CacheRequest:
    """Request for cache operations."""

    action: str  # "list" | "get" | "evict" | "clear"
    key: str | None = None  # Required for "get" and "evict"


@dataclass(frozen=True)
class CacheResponse:
    """Response from cache operations."""

    success: bool
    action: str
    entries: list[dict[str, Any]] | None = None  # For "list"
    entry: dict[str, Any] | None = None  # For "get"
    evicted_count: int | None = None  # For "evict" and "clear"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "success": self.success,
            "action": self.action,
            "entries": self.entries,
            "entry": self.entry,
            "evicted_count": self.evicted_count,
            "error": self.error,
        }


# =============================================================================
# Promote Contracts (Phase 5 - Stub for now)
# =============================================================================


@dataclass(frozen=True)
class PromoteRequest:
    """Request to promote an ephemeral agent to permanent."""

    cache_key: str  # Key of cached agent to promote
    agent_name: str  # Name for the permanent agent
    description: str | None = None  # Optional description


@dataclass(frozen=True)
class PromoteResponse:
    """Response from promote operation."""

    success: bool
    agent_name: str | None
    spec_path: str | None  # Path to generated spec file
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "success": self.success,
            "agent_name": self.agent_name,
            "spec_path": self.spec_path,
            "error": self.error,
        }


# =============================================================================
# Manifest Response (for @node manifest aspect)
# =============================================================================


@dataclass(frozen=True)
class FoundryManifestResponse:
    """Status manifest for the Foundry Crown Jewel."""

    cache_size: int  # Number of cached ephemeral agents
    cache_max_size: int  # Maximum cache capacity
    total_forges: int  # Total forge operations
    cache_hits: int  # Number of cache hits
    cache_hit_rate: float  # Hit rate percentage
    recent_forges: list[dict[str, Any]]  # Last N forge operations
    status: str  # "operational" | "degraded" | "error"

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": "foundry_manifest",
            "cache_size": self.cache_size,
            "cache_max_size": self.cache_max_size,
            "total_forges": self.total_forges,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hit_rate,
            "recent_forges": self.recent_forges,
            "status": self.status,
        }

    def to_text(self) -> str:
        """Human-readable text for CLI/TUI."""
        lines = [
            "Foundry Status",
            "==============",
            f"Cache: {self.cache_size}/{self.cache_max_size} entries",
            f"Total Forges: {self.total_forges}",
            f"Cache Hits: {self.cache_hits} ({self.cache_hit_rate:.1%})",
            f"Status: {self.status}",
        ]
        if self.recent_forges:
            lines.append("")
            lines.append("Recent Forges:")
            for forge in self.recent_forges[:5]:
                intent = forge.get("intent", "?")[:40]
                target = forge.get("target", "?")
                lines.append(f"  - {intent}... -> {target}")
        return "\n".join(lines)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Forge
    "ForgeRequest",
    "ForgeResponse",
    # Inspect
    "InspectRequest",
    "InspectResponse",
    # Cache
    "CacheRequest",
    "CacheResponse",
    # Promote
    "PromoteRequest",
    "PromoteResponse",
    # Manifest
    "FoundryManifestResponse",
]
