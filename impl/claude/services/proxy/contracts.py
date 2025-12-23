"""
Proxy Handle Contracts: Request/Response types for AGENTESE node.

AD-015: Proxy Handles & Transparent Batch Processes

These contracts define the typed interface for the ProxyNode.
All transports (HTTP, WebSocket, CLI) collapse to these shapes.

AGENTESE: services.proxy.contracts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# =============================================================================
# Response Types (used for aspects that only return data)
# =============================================================================


@dataclass(frozen=True)
class ProxyManifestResponse:
    """Response for manifest aspect — store status."""

    total_handles: int
    fresh_count: int
    stale_count: int
    computing_count: int
    error_count: int
    reactor_wired: bool
    reactor_event_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "proxy_manifest",
            "total_handles": self.total_handles,
            "fresh_count": self.fresh_count,
            "stale_count": self.stale_count,
            "computing_count": self.computing_count,
            "error_count": self.error_count,
            "reactor_wired": self.reactor_wired,
            "reactor_event_count": self.reactor_event_count,
        }


@dataclass(frozen=True)
class HandleSummary:
    """Summary of a single proxy handle."""

    handle_id: str
    source_type: str
    human_label: str
    status: str
    is_fresh: bool
    created_at: str  # ISO format
    expires_at: str | None
    access_count: int
    computation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "handle_id": self.handle_id,
            "source_type": self.source_type,
            "human_label": self.human_label,
            "status": self.status,
            "is_fresh": self.is_fresh,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "computation_count": self.computation_count,
        }


@dataclass(frozen=True)
class ListHandlesResponse:
    """Response for list aspect."""

    handles: tuple[HandleSummary, ...]
    total_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "proxy_list",
            "handles": [h.to_dict() for h in self.handles],
            "total_count": self.total_count,
        }


@dataclass(frozen=True)
class GetHandleResponse:
    """Response for get aspect."""

    found: bool
    handle: HandleSummary | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": "proxy_get",
            "found": self.found,
        }
        if self.handle:
            result["handle"] = self.handle.to_dict()
        if self.error:
            result["error"] = self.error
        return result


@dataclass(frozen=True)
class InvalidateResponse:
    """Response for invalidate aspect."""

    success: bool
    source_type: str
    was_fresh: bool = False
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "proxy_invalidate",
            "success": self.success,
            "source_type": self.source_type,
            "was_fresh": self.was_fresh,
            "message": self.message,
        }


@dataclass(frozen=True)
class ComputeResponse:
    """Response for compute aspect."""

    success: bool
    source_type: str
    handle_id: str | None = None
    duration: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "type": "proxy_compute",
            "success": self.success,
            "source_type": self.source_type,
        }
        if self.handle_id:
            result["handle_id"] = self.handle_id
        if self.duration:
            result["duration"] = self.duration
        if self.error:
            result["error"] = self.error
        return result


@dataclass(frozen=True)
class ReactorStatusResponse:
    """Response for reactor status aspect."""

    is_wired: bool
    trigger_count: int
    subscription_count: int
    event_count: int
    invalidation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "proxy_reactor_status",
            "is_wired": self.is_wired,
            "trigger_count": self.trigger_count,
            "subscription_count": self.subscription_count,
            "event_count": self.event_count,
            "invalidation_count": self.invalidation_count,
        }


# =============================================================================
# Request Types (used for aspects that need input)
# =============================================================================


@dataclass
class GetHandleRequest:
    """Request for get aspect."""

    source_type: str


@dataclass
class InvalidateRequest:
    """Request for invalidate aspect."""

    source_type: str


@dataclass
class ComputeRequest:
    """Request for compute aspect."""

    source_type: str
    force: bool = False


# =============================================================================
# Rendering Classes
# =============================================================================


@dataclass(frozen=True)
class ProxyManifestRendering:
    """Rendering for proxy store manifest."""

    manifest: ProxyManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return self.manifest.to_dict()

    def to_text(self) -> str:
        m = self.manifest
        lines = [
            "╔═══════════════════════════════════════╗",
            "║       PROXY HANDLE STORE STATUS       ║",
            "╠═══════════════════════════════════════╣",
            f"║  Total Handles:     {m.total_handles:>15}  ║",
            f"║    Fresh:           {m.fresh_count:>15}  ║",
            f"║    Stale:           {m.stale_count:>15}  ║",
            f"║    Computing:       {m.computing_count:>15}  ║",
            f"║    Error:           {m.error_count:>15}  ║",
            "╠═══════════════════════════════════════╣",
            f"║  Reactor Wired:     {'✓ Yes' if m.reactor_wired else '✗ No':>15}  ║",
            f"║  Events Processed:  {m.reactor_event_count:>15}  ║",
            "╚═══════════════════════════════════════╝",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class HandleListRendering:
    """Rendering for handle list."""

    response: ListHandlesResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        if not self.response.handles:
            return "No proxy handles. Use `compute` to create one."

        lines = ["PROXY HANDLES", "=" * 60]
        for h in self.response.handles:
            status_icon = "●" if h.is_fresh else "○"
            lines.append(
                f"{status_icon} [{h.status:>10}] {h.source_type:<20} "
                f"(accesses: {h.access_count}, computes: {h.computation_count})"
            )
            lines.append(f"    {h.human_label}")
            lines.append("")

        lines.append(f"Total: {self.response.total_count} handles")
        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Response types
    "ProxyManifestResponse",
    "HandleSummary",
    "ListHandlesResponse",
    "GetHandleResponse",
    "InvalidateResponse",
    "ComputeResponse",
    "ReactorStatusResponse",
    # Request types
    "GetHandleRequest",
    "InvalidateRequest",
    "ComputeRequest",
    # Renderings
    "ProxyManifestRendering",
    "HandleListRendering",
]
