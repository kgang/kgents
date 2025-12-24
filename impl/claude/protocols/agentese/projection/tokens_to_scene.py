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
    Section,
    SectionType,
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
    # New token types (robustification)
    MARKDOWN_TABLE = "MARKDOWN_TABLE"  # Table with export/edit
    LINK = "LINK"  # Hyperlink with preview
    BLOCKQUOTE = "BLOCKQUOTE"  # Quoted text block
    HORIZONTAL_RULE = "HORIZONTAL_RULE"  # Section divider
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
        # New token types
        "markdown_table": MeaningTokenKind.MARKDOWN_TABLE.value,
        "link": MeaningTokenKind.LINK.value,
        "blockquote": MeaningTokenKind.BLOCKQUOTE.value,
        "horizontal_rule": MeaningTokenKind.HORIZONTAL_RULE.value,
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
        # New token types
        "markdown_table": NodeStyle(
            background="steel",
            border="gunmetal",
        ),
        "link": NodeStyle(
            foreground="living_green",
        ),
        "blockquote": NodeStyle(
            background="soil",
            border="sage",
        ),
        "horizontal_rule": NodeStyle(
            foreground="steel",
        ),
    }
    return styles.get(token_type, NodeStyle.default())


def _parse_table_data(source_text: str) -> dict[str, Any]:
    """Parse markdown table source text into structured data."""
    lines = source_text.strip().split("\n")
    if len(lines) < 2:
        return {"columns": [], "rows": [], "row_count": 0, "column_count": 0}

    # Parse header row
    def parse_row(line: str) -> list[str]:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        return [cell.strip() for cell in line.split("|")]

    # Parse alignment from separator row
    def parse_alignment(cell: str) -> str:
        cell = cell.strip()
        if cell.startswith(":") and cell.endswith(":"):
            return "center"
        elif cell.endswith(":"):
            return "right"
        return "left"

    headers = parse_row(lines[0])
    alignments = [parse_alignment(cell) for cell in parse_row(lines[1])]

    # Ensure alignments match headers
    while len(alignments) < len(headers):
        alignments.append("left")

    columns = [{"header": h, "alignment": alignments[i], "index": i} for i, h in enumerate(headers)]

    # Parse data rows
    rows = []
    for line in lines[2:]:
        if line.strip():
            cells = parse_row(line)
            # Pad or truncate to match column count
            while len(cells) < len(columns):
                cells.append("")
            rows.append(cells[: len(columns)])

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "column_count": len(columns),
    }


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
    section_index: int | None = None,
) -> SceneNode:
    """
    Convert a TextSpan (from parser) to a SceneNode.

    Args:
        span: The TextSpan to convert (may be token or plain text)
        observer: Optional observer for affordance filtering
        section_index: Optional section index for incremental parsing (Document Proxy)

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
            section_index=section_index,
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
    groups = span.token_match.match.groups() if span.token_match.match else ()

    # Tokens with capture groups
    if token_type == "agentese_path" and len(groups) >= 1:
        token_data["path"] = groups[0]
    elif token_type == "task_checkbox" and len(groups) >= 2:
        token_data["checked"] = groups[0].lower() == "x"
        token_data["description"] = groups[1]
    elif token_type == "image" and len(groups) >= 2:
        token_data["alt_text"] = groups[0]
        token_data["src"] = groups[1]
    elif token_type == "code_block" and len(groups) >= 3:
        # Groups: 0=fence (```), 1=language, 2=code
        token_data["language"] = groups[1] or ""
        token_data["code"] = groups[2] or ""
    elif token_type == "principle_ref" and len(groups) >= 1:
        token_data["principle_number"] = int(groups[0])
    elif token_type == "requirement_ref" and len(groups) >= 1:
        token_data["requirement_id"] = groups[0]
    elif token_type == "link" and len(groups) >= 2:
        token_data["text"] = groups[0]
        token_data["url"] = groups[1]

    # Tokens that parse from source text (no capture groups needed)
    elif token_type == "markdown_table":
        # Parse table structure from source text
        token_data = _parse_table_data(span.text)
    elif token_type == "blockquote":
        token_data["content"] = span.text
    elif token_type == "horizontal_rule":
        # No specific data needed
        pass

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
        section_index=section_index,
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
    # New token types
    elif token_type == "markdown_table":
        rows = token_data.get("row_count", 0)
        cols = token_data.get("column_count", 0)
        return f"Table ({rows}×{cols})"
    elif token_type == "link":
        text = str(token_data.get("text", "link"))[:30]
        return text
    elif token_type == "blockquote":
        return "Blockquote"
    elif token_type == "horizontal_rule":
        return "───"
    return token_type


# =============================================================================
# Document → SceneGraph Conversion
# =============================================================================


def _find_section_for_position(
    position: int,
    sections: list[Section],
) -> int | None:
    """Find section index containing the given byte position."""
    for section in sections:
        if section.range_start <= position < section.range_end:
            return section.index
    return None


async def tokens_to_scene_graph(
    document: "ParsedDocument",
    observer: "Observer | None" = None,
    layout_mode: LayoutMode = LayoutMode.COMFORTABLE,
    sections: list[Section] | None = None,
) -> SceneGraph:
    """
    Convert a ParsedDocument to a SceneGraph.

    This is the main bridge function that transforms Interactive Text's
    parsed document into a SceneGraph that can be rendered by Servo.

    Args:
        document: ParsedDocument with extracted tokens
        observer: Optional observer for affordance filtering
        layout_mode: Layout density mode
        sections: Optional pre-computed sections for section_index assignment

    Returns:
        SceneGraph containing all document tokens as nodes

    Example:
        >>> doc = parse_markdown("Check `self.brain.capture`")
        >>> scene = await tokens_to_scene_graph(doc)
        >>> rendered = ServoSceneRenderer(scene)
    """
    nodes: list[SceneNode] = []

    for span in document.spans:
        # Determine section index from span position
        section_index: int | None = None
        if sections:
            section_index = _find_section_for_position(span.position.start, sections)

        node = await text_span_to_scene_node(span, observer, section_index)
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
    include_sections: bool = True,
) -> SceneGraph:
    """
    Convenience function: parse markdown and convert to SceneGraph.

    Args:
        text: Markdown text to parse
        observer: Optional observer for affordance filtering
        layout_mode: Layout density mode
        include_sections: Whether to detect sections for section_index assignment

    Returns:
        SceneGraph ready for Servo rendering
    """
    from services.interactive_text.parser import parse_markdown

    document = parse_markdown(text)

    # Detect sections if requested
    sections: list[Section] | None = None
    if include_sections:
        sections = detect_sections(text)

    return await tokens_to_scene_graph(document, observer, layout_mode, sections)


# =============================================================================
# Section Detection (Document Proxy - AD-015)
# =============================================================================


def detect_sections(content: str) -> list[Section]:
    """
    Detect semantic sections in markdown content.

    Algorithm (from spec/protocols/document-proxy.md):
    1. Headings (# to ######) always start a new section
    2. Code blocks (``` or ~~~) are atomic sections
    3. Frontmatter (---) is its own section
    4. Blank lines after paragraphs mark section boundaries
    5. Lists continue until blank line + non-list content
    6. Tables are atomic sections

    Args:
        content: Raw markdown content

    Returns:
        List of Section objects with byte ranges and hashes
    """
    import hashlib
    import re

    if not content:
        return []

    lines = content.split("\n")
    sections: list[Section] = []
    current_start = 0
    current_lines: list[str] = []
    section_index = 0

    # Track state
    in_code_block = False
    code_fence = None
    in_frontmatter = False
    in_table = False
    in_list = False
    prev_blank = False

    def _finalize_section(end_line_idx: int, section_kind: str, **kwargs: Any) -> None:
        """Finalize current section and add to list."""
        nonlocal section_index, current_start, current_lines

        if not current_lines:
            return

        # Calculate byte offsets
        section_text = "\n".join(current_lines)
        section_bytes = section_text.encode("utf-8")

        # Skip empty sections
        if len(section_bytes) == 0:
            current_lines = []
            return

        range_start = current_start
        range_end = current_start + len(section_bytes)

        # Compute hash (SHA-256[:16] like K-Block)
        section_hash = hashlib.sha256(section_bytes).hexdigest()[:16]

        # Extract section-specific fields vs section-type fields
        heading_text = kwargs.pop("heading", None)
        level = kwargs.get("level")
        language = kwargs.get("language")

        # Create section type with only its fields
        section_type = SectionType(kind=section_kind, level=level, language=language)

        sections.append(
            Section(
                index=section_index,
                range_start=range_start,
                range_end=range_end,
                section_hash=section_hash,
                section_type=section_type,
                heading=heading_text,
            )
        )

        section_index += 1
        current_start = range_end + 1  # +1 for the newline
        current_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # === FRONTMATTER ===
        if i == 0 and stripped == "---":
            # Start of frontmatter
            in_frontmatter = True
            current_lines.append(line)
            i += 1
            continue

        if in_frontmatter:
            current_lines.append(line)
            if stripped == "---":
                # End of frontmatter
                _finalize_section(i, "frontmatter")
                in_frontmatter = False
            i += 1
            continue

        # === CODE BLOCKS ===
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if not in_code_block:
                # Start code block
                if current_lines:
                    # Finalize previous section
                    _finalize_section(i - 1, "paragraph")

                in_code_block = True
                code_fence = stripped[:3]
                # Extract language
                language = stripped[3:].strip() or None
                current_lines.append(line)
            else:
                # End code block
                current_lines.append(line)
                if code_fence and stripped.startswith(code_fence):
                    # Extract language from first line
                    first_line = current_lines[0] if current_lines else ""
                    language = first_line[3:].strip() or None
                    _finalize_section(i, "code_block", language=language)
                    in_code_block = False
                    code_fence = None
            i += 1
            continue

        if in_code_block:
            current_lines.append(line)
            i += 1
            continue

        # === HEADINGS ===
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match and not in_table:
            # Finalize previous section
            if current_lines:
                _finalize_section(i - 1, "paragraph")

            # Start new heading section
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2)
            current_lines.append(line)
            _finalize_section(i, "heading", level=level, heading=heading_text)
            i += 1
            continue

        # === HORIZONTAL RULE ===
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            # Finalize previous section
            if current_lines:
                _finalize_section(i - 1, "paragraph")

            # Horizontal rule is its own section
            current_lines.append(line)
            _finalize_section(i, "horizontal_rule")
            i += 1
            continue

        # === TABLES ===
        # Table row: starts with |
        if stripped.startswith("|"):
            if not in_table:
                # Start of table
                if current_lines:
                    _finalize_section(i - 1, "paragraph")
                in_table = True
            current_lines.append(line)
            i += 1
            continue

        if in_table and not stripped.startswith("|"):
            # End of table
            _finalize_section(i - 1, "table")
            in_table = False
            # Continue processing this line

        # === LISTS ===
        # List items: start with -, *, +, or digit.
        list_match = re.match(r"^(\s*)[-*+]\s+", line) or re.match(r"^(\s*)\d+\.\s+", line)
        if list_match:
            if not in_list:
                # Start of list
                if current_lines and not prev_blank:
                    _finalize_section(i - 1, "paragraph")
                in_list = True
            current_lines.append(line)
            prev_blank = False
            i += 1
            continue

        # === BLANK LINES ===
        if not stripped:
            if in_list:
                # Blank line in list - check if list continues
                current_lines.append(line)
                prev_blank = True
                i += 1
                continue
            elif current_lines:
                # Blank line after content - potential section boundary
                current_lines.append(line)
                # Check next non-blank line to decide
                next_i = i + 1
                while next_i < len(lines) and not lines[next_i].strip():
                    current_lines.append(lines[next_i])
                    next_i += 1

                if next_i < len(lines):
                    next_line = lines[next_i]
                    next_stripped = next_line.strip()

                    # Finalize if next is heading, code block, or different content type
                    if (
                        next_stripped.startswith("#")
                        or next_stripped.startswith("```")
                        or next_stripped.startswith("~~~")
                        or re.match(r"^(-{3,}|\*{3,}|_{3,})$", next_stripped)
                    ):
                        kind = "list" if in_list else "paragraph"
                        _finalize_section(next_i - 1, kind)
                        in_list = False

                i = next_i
                prev_blank = False
                continue
            else:
                # Leading blank line - skip
                current_start += len(line.encode("utf-8")) + 1
                i += 1
                continue

        # === PARAGRAPH TEXT ===
        if in_list:
            # Non-list item after blank line in list = end of list
            if prev_blank:
                _finalize_section(i - 1, "list")
                in_list = False

        current_lines.append(line)
        prev_blank = False
        i += 1

    # Finalize last section
    if current_lines:
        kind = "list" if in_list else "code_block" if in_code_block else "paragraph"
        _finalize_section(len(lines) - 1, kind)

    return sections


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
    # Section detection
    "detect_sections",
]
