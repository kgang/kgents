"""
Dawn Cockpit Contracts: Request/Response types for AGENTESE aspects.

These frozen dataclasses define the API boundary for time.dawn.* paths.
Following the Metaphysical Fullstack pattern (AD-009), contracts are the
bridge between AGENTESE protocol and service logic.

Teaching:
    gotcha: All contracts should be frozen dataclasses for immutability.
            This prevents mutation bugs at the API boundary.
            (Evidence: test_contracts.py::test_frozen_contracts)

    gotcha: Optional fields use `= None` default, not `| None` alone.
            The `| None` is the type hint; `= None` is the default.
            (Evidence: agentese-contract-protocol.md)

See: spec/protocols/dawn-cockpit.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .focus import Bucket

# =============================================================================
# Focus Contracts
# =============================================================================


@dataclass(frozen=True)
class FocusItemResponse:
    """Single focus item in response."""

    id: str
    label: str
    target: str
    bucket: str  # Bucket.value
    added_at: str  # ISO format
    last_touched: str  # ISO format
    is_stale: bool


@dataclass(frozen=True)
class FocusListResponse:
    """Response for focus.list aspect."""

    items: tuple[FocusItemResponse, ...]
    total_count: int
    bucket_filter: str | None = None  # If filtered by bucket


@dataclass(frozen=True)
class FocusAddRequest:
    """Request for focus.add aspect."""

    target: str
    label: str | None = None
    bucket: str = "today"  # Bucket.value


@dataclass(frozen=True)
class FocusAddResponse:
    """Response for focus.add aspect."""

    item: FocusItemResponse
    success: bool = True


@dataclass(frozen=True)
class FocusRemoveRequest:
    """Request for focus.remove aspect."""

    item_id: str


@dataclass(frozen=True)
class FocusRemoveResponse:
    """Response for focus.remove aspect."""

    removed: bool
    item_id: str


@dataclass(frozen=True)
class FocusPromoteRequest:
    """Request for focus.promote aspect."""

    item_id: str


@dataclass(frozen=True)
class FocusDemoteRequest:
    """Request for focus.demote aspect."""

    item_id: str


@dataclass(frozen=True)
class FocusMoveResponse:
    """Response for promote/demote aspects."""

    item: FocusItemResponse
    previous_bucket: str
    new_bucket: str


# =============================================================================
# Snippet Contracts
# =============================================================================


@dataclass(frozen=True)
class SnippetResponse:
    """Single snippet in response."""

    id: str
    label: str
    type: str  # "static", "query", "custom"
    kind: str | None  # For static/query: voice_anchor, quote, etc.
    content: str | None  # Eagerly loaded or None if query not loaded
    is_loaded: bool = True  # For query snippets


@dataclass(frozen=True)
class SnippetListResponse:
    """Response for snippets.list aspect."""

    snippets: tuple[SnippetResponse, ...]
    total_count: int
    static_count: int
    query_count: int
    custom_count: int


@dataclass(frozen=True)
class SnippetCopyRequest:
    """Request for snippets.copy aspect."""

    snippet_id: str


@dataclass(frozen=True)
class SnippetCopyResponse:
    """Response for snippets.copy aspect."""

    snippet_id: str
    label: str
    content: str
    copied: bool = True
    witness_mark_id: str | None = None  # If Witness recorded the copy


@dataclass(frozen=True)
class SnippetAddRequest:
    """Request for snippets.add aspect (custom snippets only)."""

    label: str
    content: str


@dataclass(frozen=True)
class SnippetAddResponse:
    """Response for snippets.add aspect."""

    snippet: SnippetResponse
    success: bool = True


@dataclass(frozen=True)
class SnippetRemoveRequest:
    """Request for snippets.remove aspect (custom snippets only)."""

    snippet_id: str


@dataclass(frozen=True)
class SnippetRemoveResponse:
    """Response for snippets.remove aspect."""

    removed: bool
    snippet_id: str


# =============================================================================
# Manifest Contract
# =============================================================================


@dataclass(frozen=True)
class DawnManifestResponse:
    """Response for time.dawn.manifest aspect."""

    focus_count: int
    today_count: int
    week_count: int
    someday_count: int
    snippet_count: int
    stale_count: int
    last_coffee: str | None = None  # ISO format, if available
    session_id: str | None = None


# =============================================================================
# Helper Functions
# =============================================================================


def focus_item_to_response(item: Any) -> FocusItemResponse:
    """Convert FocusItem to FocusItemResponse."""
    return FocusItemResponse(
        id=item.id,
        label=item.label,
        target=item.target,
        bucket=item.bucket.value,
        added_at=item.added_at.isoformat(),
        last_touched=item.last_touched.isoformat(),
        is_stale=item.is_stale,
    )


def snippet_to_response(snippet: Any) -> SnippetResponse:
    """Convert any Snippet type to SnippetResponse."""
    snippet_dict = snippet.to_dict()
    return SnippetResponse(
        id=snippet_dict["id"],
        label=snippet_dict["label"],
        type=snippet_dict["type"],
        kind=snippet_dict.get("kind"),
        content=snippet_dict.get("content"),
        is_loaded=snippet_dict.get("is_loaded", True),
    )


__all__ = [
    # Focus contracts
    "FocusItemResponse",
    "FocusListResponse",
    "FocusAddRequest",
    "FocusAddResponse",
    "FocusRemoveRequest",
    "FocusRemoveResponse",
    "FocusPromoteRequest",
    "FocusDemoteRequest",
    "FocusMoveResponse",
    # Snippet contracts
    "SnippetResponse",
    "SnippetListResponse",
    "SnippetCopyRequest",
    "SnippetCopyResponse",
    "SnippetAddRequest",
    "SnippetAddResponse",
    "SnippetRemoveRequest",
    "SnippetRemoveResponse",
    # Manifest
    "DawnManifestResponse",
    # Helpers
    "focus_item_to_response",
    "snippet_to_response",
]
