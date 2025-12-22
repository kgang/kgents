"""
Outline Model for Context Perception.

The Outline is a tree of text snippets that can be navigated, expanded,
collapsed, copied, and pasted. Every operation is "normal" on the surface
but does hidden magic underneath.

Spec: spec/protocols/context-perception.md §4

Core Insight: Text snippets are the fundamental unit. Everything else—parsers,
tokens, integrations, overlays, orchestration—exists to make normal operations
contextually magical.

Teaching:
    gotcha: OutlineNode can contain either a TextSnippet OR a PortalToken.
            Use isinstance() checks or pattern matching to handle both.
            (Evidence: test_outline.py::test_node_polymorphism)

    gotcha: Outline.copy() returns a Clipboard with invisible metadata.
            When you paste, the system can create links back to the source.
            (Evidence: test_outline.py::test_copy_paste_creates_link)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.agentese.node import Observer
    from protocols.agentese.contexts.self_context import Trail, TrailStep


# === Enums ===


class SnippetType(Enum):
    """Types of snippets in an outline (§4.2)."""

    PROSE = auto()  # Plain text, editable, flows
    PORTAL_COLLAPSED = auto()  # `▶ [edge] destination` - click to expand
    PORTAL_EXPANDED = auto()  # `▼ [edge]` + nested content - click to collapse
    CODE = auto()  # Fenced block with path, syntax highlighted
    EVIDENCE = auto()  # `📎 claim (strength)` - links to ASHC
    ANNOTATION = auto()  # `💭 note` - human or agent commentary


# === Core Data Structures ===


@dataclass
class Range:
    """
    A selection range within text.

    Used for copy/paste operations to track what was selected.
    """

    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def __post_init__(self) -> None:
        if self.start_line > self.end_line:
            raise ValueError("start_line must be <= end_line")
        if self.start_line == self.end_line and self.start_col > self.end_col:
            raise ValueError("start_col must be <= end_col on same line")

    @property
    def is_empty(self) -> bool:
        return (
            self.start_line == self.end_line and self.start_col == self.end_col
        )

    def contains(self, line: int, col: int) -> bool:
        """Check if a position is within this range."""
        if line < self.start_line or line > self.end_line:
            return False
        if line == self.start_line and col < self.start_col:
            return False
        if line == self.end_line and col > self.end_col:
            return False
        return True


@dataclass
class Location:
    """
    A location within an outline.

    Used for paste operations to know where to insert.
    """

    node_path: str  # Path to the outline node
    line: int = 0  # Line within the node
    col: int = 0  # Column within the line

    def __str__(self) -> str:
        return f"{self.node_path}:{self.line}:{self.col}"


class AnnotationType(Enum):
    """Types of agent annotations (§6)."""

    NOTE = "note"  # General observation
    SUGGESTION = "suggestion"  # Proposed action
    QUESTION = "question"  # Seeking clarification
    WARNING = "warning"  # Potential issue
    EVIDENCE = "evidence"  # Supporting a claim


@dataclass
class TextSnippet:
    """
    A snippet of text with hidden metadata (§7.2).

    The visible_text is what the user sees. The metadata travels invisibly
    with copy/paste operations, enabling provenance tracking and link creation.

    Teaching:
        gotcha: TextSnippet is the atomic unit. Even code blocks and portals
                have an underlying TextSnippet for their visible representation.
                (Evidence: test_outline.py::test_snippet_as_atomic_unit)
    """

    visible_text: str
    snippet_type: SnippetType = SnippetType.PROSE

    # Provenance (invisible to user, travels with copy/paste)
    source_path: str | None = None  # Where it came from
    copied_at: datetime | None = None  # When it was copied
    copied_by: str | None = None  # Observer ID who copied it

    # Relationships
    links: list[str] = field(default_factory=list)  # Outgoing hyperedges
    evidence_ids: list[str] = field(default_factory=list)  # Linked evidence

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def with_provenance(
        self,
        source_path: str,
        observer_id: str,
    ) -> "TextSnippet":
        """Create a copy with provenance metadata set."""
        return TextSnippet(
            visible_text=self.visible_text,
            snippet_type=self.snippet_type,
            source_path=source_path,
            copied_at=datetime.now(),
            copied_by=observer_id,
            links=self.links.copy(),
            evidence_ids=self.evidence_ids.copy(),
            id=str(uuid.uuid4()),  # New ID for the copy
        )

    def add_link(self, target_path: str) -> "TextSnippet":
        """Add an outgoing link to this snippet."""
        new_links = self.links.copy()
        if target_path not in new_links:
            new_links.append(target_path)
        return TextSnippet(
            visible_text=self.visible_text,
            snippet_type=self.snippet_type,
            source_path=self.source_path,
            copied_at=self.copied_at,
            copied_by=self.copied_by,
            links=new_links,
            evidence_ids=self.evidence_ids.copy(),
            id=self.id,
        )


@dataclass
class AnnotationSnippet(TextSnippet):
    """
    An agent's annotation in the outline.

    Phase 4C: Agent Collaboration Layer.

    Annotations are special snippets that:
    - Show the agent's name/emoji
    - Have a type (note, suggestion, question, etc.)
    - Can be dismissed or converted to actions

    Rendered as: `💭 [Claude] This looks like a good pattern`
    """

    agent_id: str = ""
    agent_name: str = ""
    annotation_type: AnnotationType = AnnotationType.NOTE
    dismissed: bool = False
    converted_to_action: bool = False

    def __post_init__(self) -> None:
        """Set snippet type to ANNOTATION."""
        self.snippet_type = SnippetType.ANNOTATION

    @property
    def emoji(self) -> str:
        """Emoji for annotation type."""
        return {
            AnnotationType.NOTE: "💭",
            AnnotationType.SUGGESTION: "💡",
            AnnotationType.QUESTION: "❓",
            AnnotationType.WARNING: "⚠️",
            AnnotationType.EVIDENCE: "📎",
        }[self.annotation_type]

    def render(self) -> str:
        """Render annotation for display."""
        return f"{self.emoji} [{self.agent_name}] {self.visible_text}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/frontend."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "annotation_type": self.annotation_type.value,
            "visible_text": self.visible_text,
            "source_path": self.source_path,
            "dismissed": self.dismissed,
            "converted_to_action": self.converted_to_action,
            "emoji": self.emoji,
            "rendered": self.render(),
        }


@dataclass
class PortalToken:
    """
    An expandable hyperedge rendered as a collapsible section.

    When collapsed: Shows `▶ [edge_type] destination_summary`
    When expanded: Shows `▼ [edge_type]` + nested content

    This is the UX projection of a hyperedge in the typed-hypergraph.

    Implements: protocols.portal_protocol.PortalTokenProtocol

    Teaching:
        gotcha: PortalToken.content is lazy-loaded. It's None until the
                portal is expanded for the first time.
                (Evidence: test_outline.py::test_portal_lazy_loading)

        gotcha: This class implements PortalTokenProtocol via structural typing.
                The 'path' and 'is_expanded' properties provide protocol compliance.
                (Evidence: test_portal_protocol.py::test_outline_satisfies_protocol)
    """

    source_path: str  # AGENTESE path of the source node
    edge_type: str  # The hyperedge type (e.g., "tests", "implements")
    destinations: list[str]  # AGENTESE paths of destination nodes

    # State
    expanded: bool = False
    depth: int = 0  # Nesting level

    # Lazy-loaded content
    _content: dict[str, str] | None = field(default=None, repr=False)

    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # =========================================================================
    # PortalTokenProtocol Implementation (structural typing)
    # =========================================================================

    @property
    def path(self) -> str:
        """
        Primary destination path (protocol compliance).

        Returns the first destination, or empty string if no destinations.
        """
        return self.destinations[0] if self.destinations else ""

    @property
    def is_expanded(self) -> bool:
        """
        Whether the portal is currently expanded (protocol compliance).

        Alias for the 'expanded' attribute.
        """
        return self.expanded

    def to_dict(self) -> dict[str, Any]:
        """
        JSON-serializable representation (protocol compliance).

        Returns:
            Dict with all portal state for API/frontend consumption
        """
        return {
            "id": self.id,
            "source_path": self.source_path,
            "edge_type": self.edge_type,
            "destinations": self.destinations,
            "path": self.path,  # Protocol field
            "is_expanded": self.is_expanded,  # Protocol field
            "expanded": self.expanded,
            "depth": self.depth,
            "destination_count": self.destination_count,
            "summary": self.summary,
            "has_content": self._content is not None,
        }

    @property
    def destination_count(self) -> int:
        return len(self.destinations)

    @property
    def summary(self) -> str:
        """Human-readable summary of destinations."""
        count = self.destination_count
        if count == 0:
            return "(empty)"
        elif count == 1:
            # Show the single destination
            return self.destinations[0].split(".")[-1]
        else:
            return f"{count} files"

    def render_collapsed(self) -> str:
        """Render as collapsed portal."""
        return f"▶ [{self.edge_type}] ──→ {self.summary}"

    def render_expanded(self) -> str:
        """Render as expanded portal header."""
        return f"▼ [{self.edge_type}] ──→ {self.summary}"

    def set_content(self, content: dict[str, str]) -> None:
        """Set the lazy-loaded content."""
        object.__setattr__(self, "_content", content)

    def get_content(self, path: str) -> str | None:
        """Get content for a specific destination."""
        if self._content is None:
            return None
        return self._content.get(path)


@dataclass
class OutlineNode:
    """
    A node in the outline tree.

    Each node contains either a TextSnippet or a PortalToken, plus
    children for nested content.

    Teaching:
        gotcha: OutlineNode is the tree structure. TextSnippet/PortalToken
                are the content. Don't confuse the container with the contained.
                (Evidence: test_outline.py::test_node_contains_snippet_or_portal)
    """

    # Content (one of these will be set)
    snippet: TextSnippet | None = None
    portal: PortalToken | None = None

    # Tree structure
    children: list["OutlineNode"] = field(default_factory=list)
    parent: "OutlineNode | None" = field(default=None, repr=False)

    # Display state
    collapsed: bool = False  # For prose sections that can collapse
    depth: int = 0

    # Identity
    path: str = ""  # Path within the outline (e.g., "root.tests.0")

    def __post_init__(self) -> None:
        if self.snippet is None and self.portal is None:
            raise ValueError("OutlineNode must have either snippet or portal")
        if self.snippet is not None and self.portal is not None:
            raise ValueError("OutlineNode cannot have both snippet and portal")

    @property
    def content_type(self) -> str:
        """Return the type of content this node holds."""
        if self.snippet is not None:
            return "snippet"
        return "portal"

    @property
    def is_expanded(self) -> bool:
        """Check if this node is expanded (for portals)."""
        if self.portal is not None:
            return self.portal.expanded
        return not self.collapsed

    @property
    def visible_text(self) -> str:
        """Get the visible text for this node."""
        if self.snippet is not None:
            return self.snippet.visible_text
        elif self.portal is not None:
            if self.portal.expanded:
                return self.portal.render_expanded()
            return self.portal.render_collapsed()
        return ""

    def add_child(self, child: "OutlineNode") -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        child.path = f"{self.path}.{len(self.children)}" if self.path else str(len(self.children))
        self.children.append(child)

    def find_node(self, path: str) -> "OutlineNode | None":
        """Find a node by path."""
        if self.path == path:
            return self
        for child in self.children:
            found = child.find_node(path)
            if found is not None:
                return found
        return None


@dataclass
class Clipboard:
    """
    Clipboard content with invisible metadata.

    When you copy text, the Clipboard captures not just the visible text
    but also provenance information that can be used when pasting.

    Law 11.3: paste(copy(snippet)).source ≡ snippet.path
    """

    visible_text: str

    # Provenance
    source_path: str  # Where the text came from
    source_range: Range  # What was selected
    copied_at: datetime = field(default_factory=datetime.now)
    copied_by: str = ""  # Observer ID

    # The original snippet (if from our system)
    original_snippet: TextSnippet | None = None

    def to_snippet(self) -> TextSnippet:
        """Convert clipboard to a TextSnippet with provenance."""
        return TextSnippet(
            visible_text=self.visible_text,
            source_path=self.source_path,
            copied_at=self.copied_at,
            copied_by=self.copied_by,
        )


@dataclass
class Outline:
    """
    A tree of text snippets representing the current view.

    The Outline is the shared workspace for human + agent collaboration.
    It projects the typed-hypergraph into editable text.

    Teaching:
        gotcha: Outline is mutable. Operations modify it in place and return
                self for chaining. Use outline.copy() for immutable semantics.
                (Evidence: test_outline.py::test_outline_mutability)
    """

    root: OutlineNode
    observer_id: str = ""

    # Navigation trail
    trail_steps: list[dict[str, Any]] = field(default_factory=list)

    # Budget tracking
    steps_taken: int = 0
    max_steps: int = 100

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def budget_remaining(self) -> float:
        """Fraction of budget remaining (0.0 to 1.0)."""
        if self.max_steps == 0:
            return 0.0
        return max(0.0, 1.0 - (self.steps_taken / self.max_steps))

    @property
    def is_budget_low(self) -> bool:
        """Check if budget is below 20%."""
        return self.budget_remaining < 0.2

    def find_node(self, path: str) -> OutlineNode | None:
        """Find a node by path."""
        return self.root.find_node(path)

    def record_step(
        self,
        action: str,
        node_path: str,
        edge_type: str | None = None,
    ) -> None:
        """Record a navigation step in the trail."""
        self.trail_steps.append({
            "action": action,
            "node_path": node_path,
            "edge_type": edge_type,
            "timestamp": datetime.now().isoformat(),
        })
        self.steps_taken += 1


# === Operations ===


class OutlineOperations:
    """
    Normal operations with hidden magic (§4.3).

    Each operation looks like a normal text operation but does more:
    - expand: Hyperedge traversal, lazy load, trail step recorded
    - collapse: Content hidden, attention freed, collapse recorded
    - copy: Invisible metadata attached (source, timestamp, observer)
    - paste: Link creation, evidence record
    - navigate: Focus shift, breadcrumb update, backtrack target
    - link: Bidirectional hyperedge created

    Teaching:
        gotcha: All operations are async because they may involve I/O
                (loading content, creating evidence, persisting trail).
                (Evidence: test_outline.py::test_operations_are_async)
    """

    def __init__(self, outline: Outline, observer_id: str = ""):
        self.outline = outline
        self.observer_id = observer_id

    async def expand(self, portal_path: str) -> bool:
        """
        Expand a portal.

        Surface: User clicks ▶ to expand
        Magic: Hyperedge traversal, content lazy-loaded,
               trail step recorded, evidence created

        Returns True if expansion succeeded.
        """
        node = self.outline.find_node(portal_path)
        if node is None or node.portal is None:
            return False

        portal = node.portal
        if portal.expanded:
            return True  # Already expanded (idempotent)

        # Lazy load content if needed
        if portal._content is None:
            content = await self._load_portal_content(portal)
            portal.set_content(content)

        # Expand
        portal.expanded = True

        # Record in trail
        self.outline.record_step(
            action="expand",
            node_path=portal_path,
            edge_type=portal.edge_type,
        )

        return True

    async def collapse(self, portal_path: str) -> bool:
        """
        Collapse a portal.

        Surface: User clicks ▼ to collapse
        Magic: Content hidden (not deleted), attention freed,
               collapse recorded in trail
        """
        node = self.outline.find_node(portal_path)
        if node is None or node.portal is None:
            return False

        portal = node.portal
        if not portal.expanded:
            return True  # Already collapsed (idempotent)

        # Collapse
        portal.expanded = False

        # Record in trail
        self.outline.record_step(
            action="collapse",
            node_path=portal_path,
            edge_type=portal.edge_type,
        )

        return True

    async def copy(self, node_path: str, selection: Range) -> Clipboard:
        """
        Copy text with provenance.

        Surface: Cmd+C copies text
        Magic: Invisible metadata attached—source path,
               timestamp, observer who copied
        """
        node = self.outline.find_node(node_path)
        if node is None:
            return Clipboard(
                visible_text="",
                source_path=node_path,
                source_range=selection,
                copied_by=self.observer_id,
            )

        # Extract visible text from selection
        text = node.visible_text
        lines = text.split("\n")

        # Extract selected portion
        if selection.start_line == selection.end_line:
            if selection.start_line < len(lines):
                line = lines[selection.start_line]
                selected = line[selection.start_col:selection.end_col]
            else:
                selected = ""
        else:
            selected_lines = []
            for i in range(selection.start_line, min(selection.end_line + 1, len(lines))):
                line = lines[i]
                if i == selection.start_line:
                    selected_lines.append(line[selection.start_col:])
                elif i == selection.end_line:
                    selected_lines.append(line[:selection.end_col])
                else:
                    selected_lines.append(line)
            selected = "\n".join(selected_lines)

        # Create clipboard with provenance
        return Clipboard(
            visible_text=selected,
            source_path=node_path,
            source_range=selection,
            copied_by=self.observer_id,
            original_snippet=node.snippet,
        )

    async def paste(
        self,
        clipboard: Clipboard,
        target: Location,
    ) -> TextSnippet | None:
        """
        Paste with link creation.

        Surface: Cmd+V pastes text
        Magic: If clipboard has provenance, create link back.
               Record paste as evidence of "used X in Y"
        """
        target_node = self.outline.find_node(target.node_path)
        if target_node is None:
            return None

        # Create snippet from clipboard
        snippet = clipboard.to_snippet()

        # Create bidirectional link if we have provenance
        if clipboard.source_path:
            # Link from pasted content back to source
            snippet = snippet.add_link(clipboard.source_path)

            # Record the paste event
            self.outline.record_step(
                action="paste",
                node_path=target.node_path,
                edge_type="linked_from",
            )

        return snippet

    async def navigate(self, path: str) -> bool:
        """
        Navigate to a node.

        Surface: Click a path to jump there
        Magic: Focus shift recorded in trail, breadcrumb updated,
               previous location becomes backtrack target
        """
        node = self.outline.find_node(path)
        if node is None:
            return False

        # Record navigation
        self.outline.record_step(
            action="navigate",
            node_path=path,
        )

        return True

    async def link(self, source_path: str, target_path: str) -> bool:
        """
        Create a bidirectional link.

        Surface: Create a reference
        Magic: Bidirectional hyperedge created—source links to target,
               target gains "linked_by" edge back to source

        Law 11.4: link(A, B) ⟹ ∃ reverse_link(B, A)
        """
        source_node = self.outline.find_node(source_path)
        target_node = self.outline.find_node(target_path)

        if source_node is None or target_node is None:
            return False

        # Add forward link
        if source_node.snippet is not None:
            source_node.snippet = source_node.snippet.add_link(target_path)

        # Add reverse link (bidirectionality law)
        if target_node.snippet is not None:
            target_node.snippet = target_node.snippet.add_link(source_path)

        # Record link creation
        self.outline.record_step(
            action="link",
            node_path=source_path,
            edge_type="links_to",
        )

        return True

    async def _load_portal_content(
        self,
        portal: PortalToken,
    ) -> dict[str, str]:
        """
        Lazy load content for portal destinations.

        Uses FileLens for semantic naming when possible.

        Teaching:
            gotcha: FileLens provides semantic names (auth_core:validate_token)
                    instead of line numbers (monolith.py:847-920).
                    (Evidence: test_outline.py::test_lens_semantic_loading)
        """
        from pathlib import Path
        from .lens import create_lens_for_range

        content: dict[str, str] = {}
        for dest in portal.destinations:
            # Try to load as file
            path = Path(dest) if "/" in dest or dest.endswith(".py") else None
            if path and path.exists():
                try:
                    file_content = path.read_text()
                    lines = file_content.splitlines()
                    # Create a lens for the full file
                    lens = create_lens_for_range(str(path), 1, len(lines))
                    if lens and lens.visible_content:
                        content[dest] = lens.visible_content
                    else:
                        content[dest] = file_content
                except Exception as e:
                    content[dest] = f"[Error loading {dest}: {e}]"
            else:
                # Not a file path or doesn't exist
                content[dest] = f"[Content of {dest}]"
        return content


# === Factory Functions ===


def create_snippet(
    text: str,
    snippet_type: SnippetType = SnippetType.PROSE,
    source_path: str | None = None,
) -> TextSnippet:
    """Create a TextSnippet with optional source path."""
    return TextSnippet(
        visible_text=text,
        snippet_type=snippet_type,
        source_path=source_path,
    )


def create_outline(
    root_text: str = "",
    observer_id: str = "",
    max_steps: int = 100,
) -> Outline:
    """Create a new Outline with a root node."""
    root_snippet = create_snippet(root_text or "# Outline")
    root_node = OutlineNode(snippet=root_snippet, path="root")

    return Outline(
        root=root_node,
        observer_id=observer_id,
        max_steps=max_steps,
    )


__all__ = [
    # Enums
    "SnippetType",
    "AnnotationType",
    # Core data structures
    "Range",
    "Location",
    "TextSnippet",
    "AnnotationSnippet",
    "PortalToken",
    "OutlineNode",
    "Clipboard",
    "Outline",
    # Operations
    "OutlineOperations",
    # Factory functions
    "create_snippet",
    "create_outline",
]
