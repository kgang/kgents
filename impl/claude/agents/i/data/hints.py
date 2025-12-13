"""
VisualHint Protocol - Agents emit these to shape their TUI representation.

The I-gent is a browser that renders agent-emitted hints.
This makes the UI heterarchical—the agent, not the framework,
decides how to be seen.

A B-gent (Banker) can emit a table. A Y-gent (Topology) can emit a graph.
The framework renders whatever they yield.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisualHint:
    """
    A hint from an agent about how to render it.

    Agents yield these in their Flux output to customize
    their TUI representation. This is the core of the heterarchical
    UI principle: agents define their own representation.

    The I-gent dynamically injects the corresponding widget based on
    the hint type.

    Examples:
        >>> # B-gent (Banker) emits table
        >>> hint = VisualHint(
        ...     type="table",
        ...     data={"Assets": 100, "Liabilities": 50},
        ...     position="sidebar",
        ...     agent_id="b-gent-1",
        ... )

        >>> # Y-gent (Topology) emits graph
        >>> hint = VisualHint(
        ...     type="graph",
        ...     data={"nodes": ["A", "B"], "edges": [("A", "B")]},
        ...     position="main",
        ...     agent_id="y-gent-1",
        ... )

        >>> # K-gent emits density field
        >>> hint = VisualHint(
        ...     type="density",
        ...     data={"activity": 0.7, "phase": "active"},
        ...     position="main",
        ...     priority=10,
        ...     agent_id="k-gent-1",
        ... )

    Attributes:
        type: Widget type to render. One of: "density", "table", "graph",
              "sparkline", "text", "loom", "custom"
        data: Type-specific payload passed to the widget factory
        position: Where to place the widget. One of: "main", "sidebar",
                  "overlay", "footer"
        priority: Render order (higher = render first). Default 0.
        agent_id: Which agent emitted this hint
    """

    type: str
    data: dict[str, Any] = field(default_factory=dict)
    position: str = "main"
    priority: int = 0
    agent_id: str = ""

    # Valid hint types
    VALID_TYPES = {
        "density",  # DensityField widget
        "table",  # DataTable widget
        "graph",  # GraphWidget (node-edge layout)
        "sparkline",  # Sparkline widget
        "text",  # Static text
        "loom",  # BranchTree (cognitive history)
        "custom",  # Custom widget (requires factory registration)
    }

    # Valid positions
    VALID_POSITIONS = {
        "main",  # Main content area
        "sidebar",  # Sidebar panel
        "overlay",  # Modal overlay
        "footer",  # Footer area
    }

    def __post_init__(self) -> None:
        """Validate hint parameters."""
        if self.type not in self.VALID_TYPES:
            raise ValueError(
                f"Unknown hint type: {self.type!r}. "
                f"Valid types: {sorted(self.VALID_TYPES)}"
            )

        if self.position not in self.VALID_POSITIONS:
            raise ValueError(
                f"Unknown position: {self.position!r}. "
                f"Valid positions: {sorted(self.VALID_POSITIONS)}"
            )

        if not isinstance(self.data, dict):
            raise TypeError(f"data must be dict, got {type(self.data).__name__}")

        if not isinstance(self.priority, int):
            raise TypeError(f"priority must be int, got {type(self.priority).__name__}")


def validate_hint(hint: VisualHint) -> None:
    """
    Validate a VisualHint.

    Raises:
        ValueError: If hint is invalid
        TypeError: If hint has wrong type
    """
    if not isinstance(hint, VisualHint):
        raise TypeError(f"Expected VisualHint, got {type(hint).__name__}")

    # VisualHint.__post_init__ already validates
    # This is a convenience function for explicit validation
