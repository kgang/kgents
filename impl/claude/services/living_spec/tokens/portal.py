"""
PortalSpecToken: Expandable hyperedges for inline document embedding.

Portal tokens are the UX projection of hypergraph navigation. Instead of
navigating away to a linked document, the agent expands it inline as a
collapsible section.

The experience of "opening a doc inside another doc" is the experience
of opening a portal token.

State Machine:
    COLLAPSED ──Expand()──→ LOADING ──ContentLoaded()──→ EXPANDED
        ↑                                                    │
        │                    Collapse()                      │
        └────────────────────────────────────────────────────┘

Philosophy:
    "Navigation is expansion. Expansion is navigation.
     The document IS the exploration."
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Awaitable, Callable

from ..contracts import Affordance, AffordanceAction, Observer
from .base import BaseSpecToken

# -----------------------------------------------------------------------------
# Portal State Machine
# -----------------------------------------------------------------------------


class PortalState(Enum):
    """Portal expansion states."""

    COLLAPSED = auto()  # Shows summary: ▶ [tests] ──→ 3 files
    LOADING = auto()  # Fetching content
    EXPANDED = auto()  # Content visible, nested portals exposed
    ERROR = auto()  # Load failed


@dataclass(frozen=True)
class PortalTransition:
    """Result of a portal state transition."""

    new_state: PortalState
    effect: str  # "loading_started", "expansion_complete", "collapsed", "error"
    data: dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# Portal Spec Token
# -----------------------------------------------------------------------------


@dataclass
class PortalSpecToken(BaseSpecToken):
    """
    Token for expandable hyperedges (portal tokens).

    Portals represent relationships to other specs/files that can be
    expanded inline rather than navigated to. This creates a tree of
    expansions that IS the agent's exploration context.

    Key properties:
    - Inline expansion: content appears nested, not navigated to
    - Recursive: expanded content reveals more portals
    - Lazy: content loads only on expansion
    - Reversible: collapse to hide detail

    Affordances:
    - Click: Toggle expand/collapse
    - Hover: Preview destinations
    """

    # Portal-specific state
    _state: PortalState = PortalState.COLLAPSED
    _edge_type: str = ""  # "tests", "implements", "imports", etc.
    _destinations: tuple[str, ...] = ()  # Target paths
    _depth: int = 0  # Nesting level
    _content_cache: dict[str, str] = field(default_factory=dict)

    # Callbacks for loading (set by parent system)
    _content_loader: Callable[[str], Awaitable[str]] | None = field(default=None, repr=False)

    @property
    def token_type(self) -> str:
        return "portal"

    @property
    def state(self) -> PortalState:
        """Current portal state."""
        return self._state

    @property
    def edge_type(self) -> str:
        """Type of hyperedge (tests, implements, imports, etc.)."""
        return self._edge_type

    @property
    def destinations(self) -> tuple[str, ...]:
        """Target paths this portal leads to."""
        return self._destinations

    @property
    def depth(self) -> int:
        """Nesting level (0 = top-level)."""
        return self._depth

    @property
    def is_expanded(self) -> bool:
        """Whether content is currently visible."""
        return self._state == PortalState.EXPANDED

    @property
    def is_loading(self) -> bool:
        """Whether content is being fetched."""
        return self._state == PortalState.LOADING

    # -------------------------------------------------------------------------
    # State Machine
    # -------------------------------------------------------------------------

    def transition(self, action: str) -> PortalTransition:
        """
        Execute state transition.

        Valid transitions:
        - COLLAPSED + "expand" → LOADING
        - LOADING + "loaded" → EXPANDED
        - LOADING + "error" → ERROR
        - EXPANDED + "collapse" → COLLAPSED
        - ERROR + "retry" → LOADING
        - ERROR + "collapse" → COLLAPSED
        """
        transitions: dict[tuple[PortalState, str], tuple[PortalState, str]] = {
            (PortalState.COLLAPSED, "expand"): (PortalState.LOADING, "loading_started"),
            (PortalState.LOADING, "loaded"): (PortalState.EXPANDED, "expansion_complete"),
            (PortalState.LOADING, "error"): (PortalState.ERROR, "load_failed"),
            (PortalState.EXPANDED, "collapse"): (PortalState.COLLAPSED, "collapsed"),
            (PortalState.ERROR, "retry"): (PortalState.LOADING, "loading_started"),
            (PortalState.ERROR, "collapse"): (PortalState.COLLAPSED, "collapsed"),
        }

        key = (self._state, action)
        if key in transitions:
            new_state, effect = transitions[key]
            old_state = self._state
            object.__setattr__(self, "_state", new_state)
            return PortalTransition(
                new_state=new_state,
                effect=effect,
                data={"old_state": old_state.name, "action": action},
            )

        # Invalid transition — no-op
        return PortalTransition(
            new_state=self._state,
            effect="no_op",
            data={"action": action, "reason": "invalid_transition"},
        )

    async def expand(self) -> PortalTransition:
        """
        Expand the portal, loading content if needed.

        This is the high-level expand operation that:
        1. Transitions to LOADING state
        2. Fetches content for all destinations
        3. Transitions to EXPANDED state
        """
        if self._state == PortalState.EXPANDED:
            # Already expanded — idempotent
            return PortalTransition(
                new_state=PortalState.EXPANDED,
                effect="already_expanded",
            )

        # Transition to loading
        trans = self.transition("expand")
        if trans.effect != "loading_started":
            return trans

        # Load content
        try:
            if self._content_loader:
                for dest in self._destinations:
                    if dest not in self._content_cache:
                        content = await self._content_loader(dest)
                        self._content_cache[dest] = content

            # Transition to expanded
            return self.transition("loaded")

        except Exception as e:
            # Transition to error
            trans = self.transition("error")
            trans.data["error"] = str(e)
            return trans

    def collapse(self) -> PortalTransition:
        """Collapse the portal, hiding content."""
        return self.transition("collapse")

    # -------------------------------------------------------------------------
    # Affordances
    # -------------------------------------------------------------------------

    def affordance(self, observer: Observer) -> Affordance | None:
        """Toggle expand/collapse on click."""
        if self._state == PortalState.EXPANDED:
            return Affordance(
                action=AffordanceAction.EXPAND,
                label="Collapse",
                target=None,
                tooltip=f"Collapse [{self._edge_type}]",
            )
        else:
            count = len(self._destinations)
            noun = "file" if count == 1 else "files"
            return Affordance(
                action=AffordanceAction.EXPAND,
                label="Expand",
                target=None,
                tooltip=f"Expand [{self._edge_type}] → {count} {noun}",
            )

    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------

    def _render_cli(self) -> str:
        """Render for CLI with Rich formatting."""
        count = len(self._destinations)
        noun = "file" if count == 1 else "files"

        if self._state == PortalState.COLLAPSED:
            return f"▶ [blue][{self._edge_type}][/blue] ──→ {count} {noun}"
        elif self._state == PortalState.LOADING:
            return f"◐ [yellow][{self._edge_type}][/yellow] ──→ loading..."
        elif self._state == PortalState.EXPANDED:
            lines = [f"▼ [blue][{self._edge_type}][/blue] ──→ {count} {noun}"]
            indent = "  " * (self._depth + 1)
            for dest in self._destinations:
                content = self._content_cache.get(dest, "")
                preview = content[:200] + "..." if len(content) > 200 else content
                lines.append(f"{indent}┌─ {dest}")
                for line in preview.split("\n")[:5]:
                    lines.append(f"{indent}│ {line}")
                lines.append(f"{indent}└─")
            return "\n".join(lines)
        elif self._state == PortalState.ERROR:
            return f"✗ [red][{self._edge_type}][/red] ──→ error"

        return self._value

    def _render_markdown(self) -> str:
        """Render as markdown (collapsed always for roundtrip)."""
        count = len(self._destinations)
        noun = "file" if count == 1 else "files"
        return f"> ▶ [{self._edge_type}] ──→ {count} {noun}"

    def _render_web(self) -> dict[str, Any]:
        """Render as React component props."""
        return {
            **self.to_dict(),
            "state": self._state.name,
            "edge_type": self._edge_type,
            "destinations": list(self._destinations),
            "depth": self._depth,
            "is_expanded": self.is_expanded,
            "is_loading": self.is_loading,
            "content": self._content_cache if self.is_expanded else {},
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        return {
            "token_type": self.token_type,
            "span": list(self._span),
            "value": self._value,
            "state": self._state.name,
            "edge_type": self._edge_type,
            "destinations": list(self._destinations),
            "depth": self._depth,
            "metadata": self._metadata,
        }

    # -------------------------------------------------------------------------
    # Factory
    # -------------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        edge_type: str,
        destinations: list[str],
        span: tuple[int, int] = (0, 0),
        depth: int = 0,
        content_loader: Callable[[str], Awaitable[str]] | None = None,
    ) -> "PortalSpecToken":
        """
        Create a portal token from edge type and destinations.

        Args:
            edge_type: Type of hyperedge (tests, implements, imports)
            destinations: Target paths
            span: Character span in source
            depth: Nesting level
            content_loader: Async function to load destination content

        Returns:
            New PortalSpecToken in COLLAPSED state
        """
        count = len(destinations)
        noun = "file" if count == 1 else "files"
        value = f"▶ [{edge_type}] ──→ {count} {noun}"

        return cls(
            _span=span,
            _value=value,
            _state=PortalState.COLLAPSED,
            _edge_type=edge_type,
            _destinations=tuple(destinations),
            _depth=depth,
            _content_loader=content_loader,
        )


# -----------------------------------------------------------------------------
# Portal Laws
# -----------------------------------------------------------------------------

# Law 1: Expansion Idempotence
# expand(expand(portal)) ≡ expand(portal)
# Expanding an already-expanded portal is a no-op.

# Law 2: Collapse Inverse
# expand(collapse(expand(portal))) ≡ expand(portal)
# Collapsing then expanding returns to expanded state.

# Law 3: Depth Boundedness
# depth(portal) ≤ max_depth (default: 5)
# Prevents infinite expansion chains.
