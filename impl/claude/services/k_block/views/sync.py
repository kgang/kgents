"""
Bidirectional View Synchronization — Phase 3

Philosophy:
    "Edit in any view; coherence is maintained by semantic transforms."
    "The proof IS the decision. The mark IS the witness."

This module enables true bidirectional editing:
    - Prose → Graph/Code/Outline (existing, forward transforms)
    - Graph → Prose (new, inverse transform)
    - Code → Prose (new, inverse transform)
    - Outline → Prose (new, inverse transform)

The key insight: transforms are SEMANTIC, not textual. We transform
the meaning (tokens), then regenerate the prose that expresses it.

See: spec/protocols/k-block.md §4.2
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken, TokenKind

if TYPE_CHECKING:
    from ..core.kblock import KBlock
    from .base import View


# -----------------------------------------------------------------------------
# Semantic Delta — The Bridge Between Views
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SemanticDelta:
    """
    A semantic change that can be expressed in any view.

    Unlike EditDelta (which is positional), SemanticDelta captures
    the MEANING of a change. This enables bidirectional transforms:

    1. User edits Graph view (adds node)
    2. Delta captured: SemanticDelta(kind=ADD, token=heading_token)
    3. Transform applied to Prose: insert "## New Heading"
    4. Other views refresh from updated prose

    Philosophy:
        "The change is the meaning, not the characters."
    """

    kind: str  # "add", "remove", "modify", "move"
    token: SemanticToken
    old_value: str | None = None  # For modify: what it was
    new_value: str | None = None  # For modify: what it becomes
    parent_id: str | None = None  # For add: where to insert
    position_hint: int | None = None  # For add: line number hint
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def add(
        cls,
        token: SemanticToken,
        parent_id: str | None = None,
        position_hint: int | None = None,
    ) -> "SemanticDelta":
        """Create an ADD delta."""
        return cls(
            kind="add",
            token=token,
            new_value=token.value,
            parent_id=parent_id,
            position_hint=position_hint,
        )

    @classmethod
    def remove(cls, token: SemanticToken) -> "SemanticDelta":
        """Create a REMOVE delta."""
        return cls(
            kind="remove",
            token=token,
            old_value=token.value,
        )

    @classmethod
    def modify(
        cls,
        token: SemanticToken,
        new_value: str,
    ) -> "SemanticDelta":
        """Create a MODIFY delta."""
        return cls(
            kind="modify",
            token=token,
            old_value=token.value,
            new_value=new_value,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for witness traces."""
        return {
            "kind": self.kind,
            "token_id": self.token.id,
            "token_kind": self.token.kind.value,
            "token_value": self.token.value,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "parent_id": self.parent_id,
            "position_hint": self.position_hint,
            "timestamp": self.timestamp.isoformat(),
        }


# -----------------------------------------------------------------------------
# View Transform Protocol
# -----------------------------------------------------------------------------


class ViewTransform(ABC):
    """
    Protocol for bidirectional view transforms.

    Each view type implements this to enable:
    1. Extracting deltas from view-specific edits
    2. Applying deltas to canonical prose content

    The transform is semantic: it understands what the edit MEANS,
    not just what characters changed.
    """

    @property
    @abstractmethod
    def view_type(self) -> ViewType:
        """Which view this transform handles."""
        ...

    @abstractmethod
    def extract_delta(
        self,
        old_state: Any,
        new_state: Any,
    ) -> list[SemanticDelta]:
        """
        Extract semantic deltas from view-specific state change.

        Args:
            old_state: View state before edit
            new_state: View state after edit

        Returns:
            List of semantic deltas representing the change
        """
        ...

    @abstractmethod
    def apply_to_prose(
        self,
        prose_content: str,
        delta: SemanticDelta,
    ) -> str:
        """
        Apply semantic delta to prose content.

        This is the inverse transform: given a semantic change,
        produce the prose that expresses it.

        Args:
            prose_content: Current canonical prose
            delta: Semantic change to apply

        Returns:
            Updated prose content
        """
        ...


# -----------------------------------------------------------------------------
# Graph → Prose Transform
# -----------------------------------------------------------------------------


@dataclass
class GraphTransform(ViewTransform):
    """
    Transform between Graph view and Prose.

    Graph edits:
        - Add node → Insert heading/field in prose
        - Remove node → Delete heading/field from prose
        - Modify node label → Update heading/field text
        - Add edge → Insert reference [[target]]
        - Remove edge → Delete reference
    """

    @property
    def view_type(self) -> ViewType:
        return ViewType.GRAPH

    def extract_delta(
        self,
        old_state: Any,
        new_state: Any,
    ) -> list[SemanticDelta]:
        """Extract deltas from graph node/edge changes."""
        deltas: list[SemanticDelta] = []

        # old_state and new_state are GraphView instances
        old_nodes = {n.id: n for n in old_state.nodes} if hasattr(old_state, "nodes") else {}
        new_nodes = {n.id: n for n in new_state.nodes} if hasattr(new_state, "nodes") else {}

        # Detect added nodes
        for nid, node in new_nodes.items():
            if nid not in old_nodes:
                kind = TokenKind.HEADING if node.kind == "heading" else TokenKind.FIELD
                token = SemanticToken(id=nid, kind=kind, value=node.label)
                deltas.append(SemanticDelta.add(token))

        # Detect removed nodes
        for nid, node in old_nodes.items():
            if nid not in new_nodes:
                kind = TokenKind.HEADING if node.kind == "heading" else TokenKind.FIELD
                token = SemanticToken(id=nid, kind=kind, value=node.label)
                deltas.append(SemanticDelta.remove(token))

        # Detect modified nodes (same id, different label)
        for nid, new_node in new_nodes.items():
            if nid in old_nodes:
                old_node = old_nodes[nid]
                if old_node.label != new_node.label:
                    kind = TokenKind.HEADING if old_node.kind == "heading" else TokenKind.FIELD
                    token = SemanticToken(id=nid, kind=kind, value=old_node.label)
                    deltas.append(SemanticDelta.modify(token, new_node.label))

        return deltas

    def apply_to_prose(
        self,
        prose_content: str,
        delta: SemanticDelta,
    ) -> str:
        """Apply graph delta to prose."""
        lines = prose_content.split("\n")

        if delta.kind == "add":
            return self._apply_add(lines, delta)
        elif delta.kind == "remove":
            return self._apply_remove(lines, delta)
        elif delta.kind == "modify":
            return self._apply_modify(lines, delta)

        return prose_content

    def _apply_add(self, lines: list[str], delta: SemanticDelta) -> str:
        """Insert heading or field."""
        if delta.token.kind == TokenKind.HEADING:
            # Determine heading level from id pattern (h-N)
            level = 2  # Default to ## for new headings
            new_line = f"{'#' * level} {delta.new_value or delta.token.value}"

            # Insert at position hint or end
            if delta.position_hint is not None and delta.position_hint < len(lines):
                lines.insert(delta.position_hint, new_line)
            else:
                lines.append("")
                lines.append(new_line)

        elif delta.token.kind == TokenKind.FIELD:
            new_line = f"- {delta.new_value or delta.token.value}: string"

            if delta.position_hint is not None and delta.position_hint < len(lines):
                lines.insert(delta.position_hint, new_line)
            else:
                lines.append(new_line)

        return "\n".join(lines)

    def _apply_remove(self, lines: list[str], delta: SemanticDelta) -> str:
        """Remove heading or field."""
        new_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            should_remove = False

            if delta.token.kind == TokenKind.HEADING:
                # Check if this is the heading to remove
                if stripped.startswith("#"):
                    heading_text = stripped.lstrip("#").strip()
                    if heading_text == delta.old_value:
                        should_remove = True

            elif delta.token.kind == TokenKind.FIELD:
                # Check if this is the field to remove
                if stripped.startswith("-") and ":" in stripped:
                    field_name = stripped.lstrip("-").split(":")[0].strip()
                    if field_name == delta.old_value:
                        should_remove = True

            if not should_remove:
                new_lines.append(line)

        return "\n".join(new_lines)

    def _apply_modify(self, lines: list[str], delta: SemanticDelta) -> str:
        """Modify heading or field text."""
        new_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            modified_line = line

            if delta.token.kind == TokenKind.HEADING:
                if stripped.startswith("#"):
                    heading_text = stripped.lstrip("#").strip()
                    if heading_text == delta.old_value:
                        # Preserve heading level
                        level = len(stripped) - len(stripped.lstrip("#"))
                        modified_line = f"{'#' * level} {delta.new_value}"

            elif delta.token.kind == TokenKind.FIELD:
                if stripped.startswith("-") and ":" in stripped:
                    parts = stripped.lstrip("-").split(":", 1)
                    field_name = parts[0].strip()
                    if field_name == delta.old_value:
                        # Preserve type after colon
                        type_part = parts[1].strip() if len(parts) > 1 else "string"
                        modified_line = f"- {delta.new_value}: {type_part}"

            new_lines.append(modified_line)

        return "\n".join(new_lines)


# -----------------------------------------------------------------------------
# Code → Prose Transform
# -----------------------------------------------------------------------------


@dataclass
class CodeTransform(ViewTransform):
    """
    Transform between Code view and Prose.

    Code edits:
        - Add field → Insert "- name: type" in prose
        - Remove field → Delete field line from prose
        - Modify field → Update field name or type
        - Change class name → Update first heading
    """

    @property
    def view_type(self) -> ViewType:
        return ViewType.CODE

    def extract_delta(
        self,
        old_state: Any,
        new_state: Any,
    ) -> list[SemanticDelta]:
        """Extract deltas from code field changes."""
        deltas: list[SemanticDelta] = []

        # old_state and new_state are CodeView instances
        old_fields = {f.name: f for f in old_state.fields} if hasattr(old_state, "fields") else {}
        new_fields = {f.name: f for f in new_state.fields} if hasattr(new_state, "fields") else {}

        # Class name change
        old_class = getattr(old_state, "_class_name", "GeneratedType")
        new_class = getattr(new_state, "_class_name", "GeneratedType")
        if old_class != new_class and new_class != "GeneratedType":
            token = SemanticToken(id=f"t-{old_class}", kind=TokenKind.TYPE, value=old_class)
            deltas.append(SemanticDelta.modify(token, new_class))

        # Detect added fields
        for name, fld in new_fields.items():
            if name not in old_fields:
                token = SemanticToken(id=f"f-{name}", kind=TokenKind.FIELD, value=name)
                # Store type hint in metadata
                deltas.append(
                    SemanticDelta(
                        kind="add",
                        token=token,
                        new_value=f"{name}: {fld.type_hint}",
                    )
                )

        # Detect removed fields
        for name, fld in old_fields.items():
            if name not in new_fields:
                token = SemanticToken(id=f"f-{name}", kind=TokenKind.FIELD, value=name)
                deltas.append(SemanticDelta.remove(token))

        # Detect modified fields
        for name, new_fld in new_fields.items():
            if name in old_fields:
                old_fld = old_fields[name]
                if old_fld.type_hint != new_fld.type_hint:
                    token = SemanticToken(id=f"f-{name}", kind=TokenKind.FIELD, value=name)
                    deltas.append(
                        SemanticDelta(
                            kind="modify",
                            token=token,
                            old_value=f"{name}: {old_fld.type_hint}",
                            new_value=f"{name}: {new_fld.type_hint}",
                        )
                    )

        return deltas

    def apply_to_prose(
        self,
        prose_content: str,
        delta: SemanticDelta,
    ) -> str:
        """Apply code delta to prose."""
        lines = prose_content.split("\n")

        if delta.kind == "add":
            # Add new field line
            field_line = f"- {delta.new_value}"

            # Find last field line and insert after
            last_field_idx = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("-") and ":" in line:
                    last_field_idx = i

            if last_field_idx >= 0:
                lines.insert(last_field_idx + 1, field_line)
            else:
                lines.append(field_line)

        elif delta.kind == "remove":
            # Remove field line
            lines = [
                line
                for line in lines
                if not (
                    line.strip().startswith("-")
                    and ":" in line
                    and line.strip().lstrip("-").split(":")[0].strip() == delta.old_value
                )
            ]

        elif delta.kind == "modify":
            # Modify field or class name
            if delta.token.kind == TokenKind.TYPE:
                # Update first heading
                for i, line in enumerate(lines):
                    if line.strip().startswith("#"):
                        level = len(line) - len(line.lstrip("#"))
                        lines[i] = f"{'#' * level} {delta.new_value}"
                        break
            else:
                # Update field
                for i, line in enumerate(lines):
                    if line.strip().startswith("-") and ":" in line:
                        parts = line.strip().lstrip("-").split(":", 1)
                        if parts[0].strip() == delta.token.value:
                            # Parse new_value for name and type
                            new_parts = (
                                delta.new_value.split(":")
                                if delta.new_value
                                else [delta.token.value, "string"]
                            )
                            new_name = new_parts[0].strip()
                            new_type = new_parts[1].strip() if len(new_parts) > 1 else "string"
                            lines[i] = f"- {new_name}: {new_type}"
                            break

        return "\n".join(lines)


# -----------------------------------------------------------------------------
# Outline → Prose Transform
# -----------------------------------------------------------------------------


@dataclass
class OutlineTransform(ViewTransform):
    """
    Transform between Outline view and Prose.

    Outline edits:
        - Add heading → Insert heading in prose
        - Remove heading → Delete heading from prose
        - Modify heading → Update heading text
        - Reorder → Move heading (complex, not yet supported)
    """

    @property
    def view_type(self) -> ViewType:
        return ViewType.OUTLINE

    def extract_delta(
        self,
        old_state: Any,
        new_state: Any,
    ) -> list[SemanticDelta]:
        """Extract deltas from outline heading changes."""
        deltas: list[SemanticDelta] = []

        # Get headings from both states
        old_headings = self._extract_headings(old_state)
        new_headings = self._extract_headings(new_state)

        # Detect added headings
        for hid, (level, text) in new_headings.items():
            if hid not in old_headings:
                token = SemanticToken(id=hid, kind=TokenKind.HEADING, value=text)
                deltas.append(SemanticDelta.add(token))

        # Detect removed headings
        for hid, (level, text) in old_headings.items():
            if hid not in new_headings:
                token = SemanticToken(id=hid, kind=TokenKind.HEADING, value=text)
                deltas.append(SemanticDelta.remove(token))

        # Detect modified headings
        for hid, (new_level, new_text) in new_headings.items():
            if hid in old_headings:
                old_level, old_text = old_headings[hid]
                if old_text != new_text:
                    token = SemanticToken(id=hid, kind=TokenKind.HEADING, value=old_text)
                    deltas.append(SemanticDelta.modify(token, new_text))

        return deltas

    def _extract_headings(self, state: Any) -> dict[str, tuple[int, str]]:
        """Extract heading id -> (level, text) from outline state."""
        result: dict[str, tuple[int, str]] = {}

        if hasattr(state, "_headings"):
            for h in state._headings:
                result[h.id] = (h.level, h.text)
        elif hasattr(state, "tokens"):
            for t in state.tokens():
                if t.kind == TokenKind.HEADING:
                    # Infer level from id or default to 1
                    result[t.id] = (1, t.value)

        return result

    def apply_to_prose(
        self,
        prose_content: str,
        delta: SemanticDelta,
    ) -> str:
        """Apply outline delta to prose (same as graph for headings)."""
        # Reuse graph transform logic for headings
        graph_transform = GraphTransform()
        return graph_transform.apply_to_prose(prose_content, delta)


# -----------------------------------------------------------------------------
# Transform Registry
# -----------------------------------------------------------------------------


class TransformRegistry:
    """
    Registry of bidirectional view transforms.

    Enables looking up the appropriate transform for any view type.
    """

    _instance: "TransformRegistry | None" = None
    _transforms: dict[ViewType, ViewTransform]

    def __init__(self) -> None:
        self._transforms = {
            ViewType.GRAPH: GraphTransform(),
            ViewType.CODE: CodeTransform(),
            ViewType.OUTLINE: OutlineTransform(),
        }

    @classmethod
    def get(cls) -> "TransformRegistry":
        """Get singleton registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_transform(self, view_type: ViewType) -> ViewTransform | None:
        """Get transform for view type."""
        return self._transforms.get(view_type)

    def can_transform(self, view_type: ViewType) -> bool:
        """Whether this view type supports bidirectional transform."""
        return view_type in self._transforms


# -----------------------------------------------------------------------------
# Bidirectional Sync Coordinator
# -----------------------------------------------------------------------------


@dataclass
class BidirectionalSync:
    """
    Coordinates bidirectional synchronization between views.

    This is the Phase 3 upgrade to KBlockSheaf.propagate().
    Instead of only accepting PROSE as source, it accepts
    ANY editable view and transforms changes semantically.

    Philosophy:
        "Edit anywhere, coherence everywhere."

    Usage:
        >>> sync = BidirectionalSync(kblock)
        >>> deltas = sync.apply_view_edit(ViewType.GRAPH, old_graph, new_graph)
        >>> print(f"Applied {len(deltas)} semantic changes")
    """

    kblock: "KBlock"
    registry: TransformRegistry = field(default_factory=TransformRegistry.get)

    def apply_view_edit(
        self,
        source_view: ViewType,
        old_state: Any,
        new_state: Any,
    ) -> list[SemanticDelta]:
        """
        Apply edit from any view to canonical prose.

        Args:
            source_view: Which view was edited
            old_state: View state before edit
            new_state: View state after edit

        Returns:
            List of semantic deltas that were applied

        Raises:
            ValueError: If source_view doesn't support transforms
        """
        # PROSE is canonical — just update directly
        if source_view == ViewType.PROSE:
            new_content = new_state if isinstance(new_state, str) else new_state.to_canonical()
            self.kblock.set_content(new_content)
            self.kblock.refresh_views()
            return []

        # DIFF and REFERENCES are read-only
        if source_view == ViewType.DIFF:
            raise ValueError("DIFF view is read-only and cannot be edited")
        if source_view == ViewType.REFERENCES:
            raise ValueError("REFERENCES view is read-only (discovery only)")

        # Get transform for this view
        transform = self.registry.get_transform(source_view)
        if transform is None:
            raise ValueError(f"No transform available for {source_view}")

        # Extract semantic deltas
        deltas = transform.extract_delta(old_state, new_state)

        # Apply each delta to prose
        prose = self.kblock.content
        for delta in deltas:
            prose = transform.apply_to_prose(prose, delta)

        # Update kblock and refresh all views
        self.kblock.set_content(prose)
        self.kblock.refresh_views()

        return deltas

    def can_edit(self, view_type: ViewType) -> bool:
        """
        Whether this view type supports editing.

        Returns:
            True if view is PROSE or has a registered transform
        """
        if view_type == ViewType.PROSE:
            return True
        if view_type == ViewType.DIFF:
            return False
        if view_type == ViewType.REFERENCES:
            return False  # Read-only discovery view
        return self.registry.can_transform(view_type)


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    "SemanticDelta",
    "ViewTransform",
    "GraphTransform",
    "CodeTransform",
    "OutlineTransform",
    "TransformRegistry",
    "BidirectionalSync",
]
