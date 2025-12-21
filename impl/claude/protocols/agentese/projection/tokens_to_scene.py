"""
Token-to-SceneGraph Bridge.

This module bridges Interactive Text's MeaningTokens to the SceneGraph abstraction,
enabling unified rendering through Servo.

The Bridge Pattern:
    MeaningToken[] ──tokens_to_scene_graph()──▶ SceneGraph ──Servo──▶ React

Design Philosophy (from brainstorming/2025-12-21-interactive-text-frontend-integration.md):
    - Reuse Servo — Don't create parallel rendering path
    - Preserve Affordances — Token interactions survive conversion
    - Observer Dependence — Different observers see different scenes
    - Density Awareness — COMPACT/COMFORTABLE/SPACIOUS from LayoutDirective

Token → SceneNode Mapping:
    | MeaningToken    | SceneNodeKind   | Visual             |
    |-----------------|-----------------|---------------------|
    | agentese_path   | AGENTESE_PORTAL | Glowing link       |
    | task_checkbox   | TASK_TOGGLE     | Checkbox icon      |
    | image           | IMAGE_EMBED     | Thumbnail          |
    | code_block      | CODE_REGION     | Syntax box         |
    | principle_ref   | PRINCIPLE_ANCHOR| Badge              |
    | requirement_ref | REQUIREMENT_TRACE| Badge             |

AGENTESE: self.document.scene
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from .scene import (
    Interaction,
    LayoutDirective,
    LayoutMode,
    NodeStyle,
    SceneGraph,
    SceneNode,
    SceneNodeId,
    SceneNodeKind,
    generate_node_id,
)

if TYPE_CHECKING:
    from services.interactive_text.contracts import Affordance, Observer
    from services.interactive_text.parser import ParsedDocument, TextSpan


# =============================================================================
# Extended SceneNodeKind for Meaning Tokens
# =============================================================================


class MeaningTokenKind(str, Enum):
    """
    Extended node kinds for meaning tokens.

    These extend the base SceneNodeKind to support Interactive Text tokens.
    The ServoNodeRenderer delegates to MeaningTokenRenderer for these kinds.
    """

    AGENTESE_PORTAL = "AGENTESE_PORTAL"  # AGENTESE path with navigate/hover
    TASK_TOGGLE = "TASK_TOGGLE"  # Checkbox with toggle affordance
    IMAGE_EMBED = "IMAGE_EMBED"  # Image with expand/analyze
    CODE_REGION = "CODE_REGION"  # Code block with run/edit
    PRINCIPLE_ANCHOR = "PRINCIPLE_ANCHOR"  # Principle reference badge
    REQUIREMENT_TRACE = "REQUIREMENT_TRACE"  # Requirement reference badge
    PLAIN_TEXT = "PLAIN_TEXT"  # Non-token text (markdown prose)


# =============================================================================
# Token → SceneNode Converters
# =============================================================================


@dataclass(frozen=True)
class MeaningTokenContent:
    """
    Content payload for meaning token scene nodes.

    This is the `content` field of a SceneNode when kind is a MeaningTokenKind.
    It carries all token data needed for rendering.
    """

    token_type: str  # e.g., "agentese_path", "task_checkbox"
    source_text: str  # Original text
    source_position: tuple[int, int]  # (start, end)
    token_id: str  # Unique identifier
    token_data: dict[str, Any] = field(default_factory=dict)  # Token-specific data
    affordances: list[dict[str, Any]] = field(default_factory=list)  # Serialized affordances

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "token_type": self.token_type,
            "source_text": self.source_text,
            "source_position": list(self.source_position),
            "token_id": self.token_id,
            "token_data": self.token_data,
            "affordances": self.affordances,
        }


def _token_type_to_kind(token_type: str) -> str:
    """Map token type name to MeaningTokenKind."""
    mapping = {
        "agentese_path": MeaningTokenKind.AGENTESE_PORTAL.value,
        "task_checkbox": MeaningTokenKind.TASK_TOGGLE.value,
        "image": MeaningTokenKind.IMAGE_EMBED.value,
        "code_block": MeaningTokenKind.CODE_REGION.value,
        "principle_ref": MeaningTokenKind.PRINCIPLE_ANCHOR.value,
        "requirement_ref": MeaningTokenKind.REQUIREMENT_TRACE.value,
    }
    return mapping.get(token_type, MeaningTokenKind.PLAIN_TEXT.value)


def _token_style(token_type: str) -> NodeStyle:
    """Get style for token type."""
    styles = {
        "agentese_path": NodeStyle(
            foreground="living_green",
            breathing=True,
        ),
        "task_checkbox": NodeStyle(
            background="sage",
            paper_grain=True,
        ),
        "image": NodeStyle(
            border="copper",
            unfurling=True,
        ),
        "code_block": NodeStyle(
            background="soil",
            paper_grain=True,
        ),
        "principle_ref": NodeStyle(
            background="amber",
        ),
        "requirement_ref": NodeStyle(
            background="purple",
        ),
    }
    return styles.get(token_type, NodeStyle.default())


def _affordances_to_interactions(affordances: list[dict[str, Any]]) -> tuple[Interaction, ...]:
    """Convert affordance list to Interaction tuple."""
    interactions = []
    for aff in affordances:
        if aff.get("enabled", True):
            interactions.append(
                Interaction(
                    kind=aff.get("action", "click"),
                    action=aff.get("handler", ""),
                    requires_trust=0,
                    metadata={"name": aff.get("name", "")},
                )
            )
    return tuple(interactions)


async def text_span_to_scene_node(
    span: "TextSpan",
    observer: "Observer | None" = None,
) -> SceneNode:
    """
    Convert a TextSpan (from parser) to a SceneNode.

    Args:
        span: The TextSpan to convert (may be token or plain text)
        observer: Optional observer for affordance filtering

    Returns:
        SceneNode representing the span
    """
    if not span.is_token or not span.token_match:
        # Plain text span
        return SceneNode(
            id=generate_node_id(),
            kind=SceneNodeKind.TEXT,
            content=span.text,
            label="",
            metadata={
                "meaning_token_kind": MeaningTokenKind.PLAIN_TEXT.value,
                "source_position": [span.position.start, span.position.end],
            },
        )

    # Get token definition
    defn = span.token_match.definition
    token_type = defn.name

    # Build affordance list (serialized)
    affordances_data: list[dict[str, Any]] = []
    for aff in defn.affordances:
        affordances_data.append(aff.to_dict())

    # Extract token-specific data from match groups
    token_data: dict[str, Any] = {}
    if span.token_match.match.groups():
        groups = span.token_match.match.groups()
        if token_type == "agentese_path" and len(groups) >= 1:
            token_data["path"] = groups[0]
        elif token_type == "task_checkbox" and len(groups) >= 2:
            token_data["checked"] = groups[0].lower() == "x"
            token_data["description"] = groups[1]
        elif token_type == "image" and len(groups) >= 2:
            token_data["alt_text"] = groups[0]
            token_data["src"] = groups[1]
        elif token_type == "code_block" and len(groups) >= 2:
            token_data["language"] = groups[0]
            token_data["code"] = groups[1]
        elif token_type == "principle_ref" and len(groups) >= 1:
            token_data["principle_number"] = int(groups[0])
        elif token_type == "requirement_ref" and len(groups) >= 1:
            token_data["requirement_id"] = groups[0]

    # Build content
    content = MeaningTokenContent(
        token_type=token_type,
        source_text=span.text,
        source_position=(span.position.start, span.position.end),
        token_id=f"{token_type}:{span.position.start}:{span.position.end}",
        token_data=token_data,
        affordances=affordances_data,
    )

    # Build SceneNode
    # We use SceneNodeKind.TEXT but store the actual kind in metadata
    # This allows Servo to render while we add proper kind support
    return SceneNode(
        id=generate_node_id(),
        kind=SceneNodeKind.TEXT,  # Use TEXT as fallback, kind in metadata
        content=content.to_dict(),
        label=_get_token_label(token_type, token_data),
        style=_token_style(token_type),
        interactions=_affordances_to_interactions(affordances_data),
        metadata={
            "meaning_token_kind": _token_type_to_kind(token_type),
            "token_type": token_type,
            "source_position": [span.position.start, span.position.end],
        },
    )


def _get_token_label(token_type: str, token_data: dict[str, Any]) -> str:
    """Get human-readable label for token."""
    if token_type == "agentese_path":
        return str(token_data.get("path", "AGENTESE path"))
    elif token_type == "task_checkbox":
        checked = "✓" if token_data.get("checked") else "○"
        desc = str(token_data.get("description", ""))[:30]
        return f"{checked} {desc}"
    elif token_type == "image":
        return str(token_data.get("alt_text", "Image"))[:30]
    elif token_type == "code_block":
        lang = token_data.get("language", "code")
        return f"```{lang}```"
    elif token_type == "principle_ref":
        num = token_data.get("principle_number", "?")
        return f"[P{num}]"
    elif token_type == "requirement_ref":
        req_id = token_data.get("requirement_id", "?")
        return f"[R{req_id}]"
    return token_type


# =============================================================================
# Document → SceneGraph Conversion
# =============================================================================


async def tokens_to_scene_graph(
    document: "ParsedDocument",
    observer: "Observer | None" = None,
    layout_mode: LayoutMode = LayoutMode.COMFORTABLE,
) -> SceneGraph:
    """
    Convert a ParsedDocument to a SceneGraph.

    This is the main bridge function that transforms Interactive Text's
    parsed document into a SceneGraph that can be rendered by Servo.

    Args:
        document: ParsedDocument with extracted tokens
        observer: Optional observer for affordance filtering
        layout_mode: Layout density mode

    Returns:
        SceneGraph containing all document tokens as nodes

    Example:
        >>> doc = parse_markdown("Check `self.brain.capture`")
        >>> scene = await tokens_to_scene_graph(doc)
        >>> rendered = ServoSceneRenderer(scene)
    """
    nodes: list[SceneNode] = []

    for span in document.spans:
        node = await text_span_to_scene_node(span, observer)
        nodes.append(node)

    # Create layout directive based on document structure
    # For markdown, vertical layout is natural
    layout = LayoutDirective.vertical(gap=0.5, mode=layout_mode)

    return SceneGraph.from_nodes(
        nodes=nodes,
        layout=layout,
    ).with_layout(layout)


async def markdown_to_scene_graph(
    text: str,
    observer: "Observer | None" = None,
    layout_mode: LayoutMode = LayoutMode.COMFORTABLE,
) -> SceneGraph:
    """
    Convenience function: parse markdown and convert to SceneGraph.

    Args:
        text: Markdown text to parse
        observer: Optional observer for affordance filtering
        layout_mode: Layout density mode

    Returns:
        SceneGraph ready for Servo rendering
    """
    from services.interactive_text.parser import parse_markdown

    document = parse_markdown(text)
    return await tokens_to_scene_graph(document, observer, layout_mode)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "MeaningTokenKind",
    "MeaningTokenContent",
    # Converters
    "text_span_to_scene_node",
    "tokens_to_scene_graph",
    "markdown_to_scene_graph",
]
