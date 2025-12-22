"""View protocol and types for K-Block hyperdimensional rendering.

Views are projections of canonical content into different modalities:
- Prose: Natural language markdown
- Graph: Concept DAG (nodes and edges)
- Code: Type definitions as Python dataclasses
- Diff: Delta from base content (read-only)
- Outline: Heading hierarchy tree
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, FrozenSet, Protocol

from .tokens import SemanticToken

if TYPE_CHECKING:
    from ..core.kblock import KBlock


class ViewType(Enum):
    """Available view types for K-Block content."""

    PROSE = "prose"  # Markdown prose (canonical, editable)
    GRAPH = "graph"  # Concept DAG (derived)
    CODE = "code"  # Type definitions (derived)
    DIFF = "diff"  # Delta from base (read-only)
    OUTLINE = "outline"  # Heading hierarchy (derived)


@dataclass(frozen=True)
class ViewDelta:
    """Base class for view-specific edit deltas.

    Each view type may extend this with specific delta information.
    """

    source_view: ViewType
    timestamp: datetime = field(default_factory=datetime.now)


class View(Protocol):
    """Protocol for K-Block views.

    Views must implement:
    - view_type: Which type of view this is
    - render(): Parse content and extract tokens
    - tokens(): Return extracted semantic tokens
    - to_canonical(): Convert back to canonical content

    Note: apply_delta() is optional since we use Prose-canonical model
    where other views are derived, not directly edited.
    """

    @property
    def view_type(self) -> ViewType:
        """Return the type of this view."""
        ...

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Render canonical content to view-specific format.

        Args:
            content: The canonical markdown content
            *args, **kwargs: View-specific arguments (e.g., base_content for DiffView)

        Returns:
            View-specific representation as string
        """
        ...

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Extract semantic tokens for sheaf coherence.

        Returns:
            Immutable set of tokens representing semantic content
        """
        ...

    def to_canonical(self) -> str:
        """Convert view state back to canonical content.

        Returns:
            Canonical markdown string
        """
        ...


def create_view(view_type: ViewType) -> View:
    """Factory function to create views by type.

    Args:
        view_type: Which view to create

    Returns:
        A fresh View instance

    Raises:
        ValueError: If view_type is not yet implemented
    """
    # Import here to avoid circular imports
    from .prose import ProseView

    match view_type:
        case ViewType.PROSE:
            return ProseView()
        case ViewType.GRAPH:
            from .graph import GraphView

            return GraphView()
        case ViewType.CODE:
            from .code import CodeView

            return CodeView()
        case ViewType.DIFF:
            from .diff import DiffView

            return DiffView()
        case ViewType.OUTLINE:
            from .outline import OutlineView

            return OutlineView()
        case _:
            raise ValueError(f"Unknown view type: {view_type}")
