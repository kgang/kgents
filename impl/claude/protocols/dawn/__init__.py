"""
Dawn Cockpit: Kent's daily operating surface.

A projection functor that composes Coffee, Witness, Portal, Brain into a
quarter-screen TUI where copy-paste is the killer feature.

Architecture:
    Dawn : (Coffee x Portal x Witness x Brain) -> TUI

The cockpit doesn't fly the plane. The pilot flies the plane.
The cockpit just makes it easy.

Three Snippet Patterns:
    StaticSnippet:  Configured, rarely changing (voice anchors, quotes)
    QuerySnippet:   AGENTESE-derived, lazy-loaded
    CustomSnippet:  User-added, ephemeral per session

Focus Buckets:
    TODAY:    1-3 items, daily cadence, stale after 36 hours
    WEEK:     3-7 items, 3-5 day cadence, stale after 7 days
    SOMEDAY:  Unbounded, monthly review, never stale

Laws (from spec):
    1. agentese_truth: AGENTESE is source of truth; symlinks are projection
    2. copy_records: Every copy action records in Witness
    3. lazy_hygiene: Hygiene checks on access, not on timer
    4. coffee_overlay: Coffee is overlay in Dawn, not separate entry
    5. three_patterns: All snippets are Static, Query, or Custom
    6. quarter_screen: Dawn never takes over; lives alongside work

Teaching:
    gotcha: AGENTESE is truth, symlinks are optional projection.
            Focus items stored via D-gent, not filesystem.
            (Evidence: spec/protocols/dawn-cockpit.md Law 1)

    gotcha: Staleness is bucket-dependent, not wall-clock.
            TODAY items stale after 36 hours.
            WEEK items stale after 7 days.
            SOMEDAY items never stale.
            (Evidence: test_focus.py::TestFocusItem::test_staleness_*)

    gotcha: QuerySnippet is frozen but uses _content for lazy caching.
            Use with_content() to create loaded version.
            (Evidence: test_snippets.py::TestQuerySnippet)

Usage:
    from protocols.dawn import FocusManager, Bucket, SnippetLibrary

    # Focus management
    manager = FocusManager()
    item = manager.add("spec/protocols/dawn-cockpit.md", label="Dawn Spec")
    manager.promote(item.id)  # Move from WEEK to TODAY

    # Snippet library
    lib = SnippetLibrary()
    lib.load_defaults()
    lib.add_custom("My Note", "Remember this important thing")

Spec Reference: spec/protocols/dawn-cockpit.md
"""

from .contracts import (
    DawnManifestResponse,
    FocusAddRequest,
    FocusAddResponse,
    FocusDemoteRequest,
    FocusItemResponse,
    FocusListResponse,
    FocusMoveResponse,
    FocusPromoteRequest,
    FocusRemoveRequest,
    FocusRemoveResponse,
    SnippetAddRequest,
    SnippetAddResponse,
    SnippetCopyRequest,
    SnippetCopyResponse,
    SnippetListResponse,
    SnippetRemoveRequest,
    SnippetRemoveResponse,
    SnippetResponse,
    focus_item_to_response,
    snippet_to_response,
)
from .focus import Bucket, FocusItem, FocusManager
from .node import (
    DAWN_AFFORDANCES,
    DawnNode,
    create_dawn_node,
    get_dawn_node,
    reset_dawn_node,
)
from .snippets import (
    CustomSnippet,
    QuerySnippet,
    Snippet,
    SnippetLibrary,
    StaticSnippet,
)
from .tui import DawnCockpit, FocusPane, GardenView, SnippetPane, run_dawn_tui

__all__ = [
    # Focus management
    "Bucket",
    "FocusItem",
    "FocusManager",
    # Snippet types
    "StaticSnippet",
    "QuerySnippet",
    "CustomSnippet",
    "Snippet",
    "SnippetLibrary",
    # Node
    "DAWN_AFFORDANCES",
    "DawnNode",
    "get_dawn_node",
    "create_dawn_node",
    "reset_dawn_node",
    # Contracts
    "DawnManifestResponse",
    "FocusItemResponse",
    "FocusListResponse",
    "FocusAddRequest",
    "FocusAddResponse",
    "FocusRemoveRequest",
    "FocusRemoveResponse",
    "FocusPromoteRequest",
    "FocusDemoteRequest",
    "FocusMoveResponse",
    "SnippetResponse",
    "SnippetListResponse",
    "SnippetCopyRequest",
    "SnippetCopyResponse",
    "SnippetAddRequest",
    "SnippetAddResponse",
    "SnippetRemoveRequest",
    "SnippetRemoveResponse",
    # Helpers
    "focus_item_to_response",
    "snippet_to_response",
    # TUI
    "DawnCockpit",
    "FocusPane",
    "SnippetPane",
    "GardenView",
    "run_dawn_tui",
]
