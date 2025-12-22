"""
Parser for Context Perception.

Recognizes meaning tokens inline in text, enabling the "normal operations
with hidden magic" paradigm. The parser identifies patterns that should
become interactive elements.

Spec: spec/protocols/context-perception.md §7

Token Types (§7.1):
    ▶ [edge] dest    - Portal (collapsed), expandable
    ▼ [edge]         - Portal (expanded), collapsible
    `path.to.thing`  - AGENTESE path, navigable
    [ ] Task         - Task checkbox, toggleable
    📎 claim         - Evidence link, opens sidebar
    @agent           - Agent mention, routes to agent

Teaching:
    gotcha: Invisible metadata is encoded as a base64 JSON suffix after
            a zero-width space. This travels with clipboard operations.
            (Evidence: test_parser.py::test_invisible_metadata_encoding)

    gotcha: extract_tokens() returns tokens in document order. Multiple
            tokens on the same line are returned left-to-right.
            (Evidence: test_parser.py::test_token_order)
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# === Token Types ===


class TokenType(Enum):
    """Types of recognized tokens in text (§7.1)."""

    PORTAL_COLLAPSED = auto()  # ▶ [edge] dest
    PORTAL_EXPANDED = auto()  # ▼ [edge]
    AGENTESE_PATH = auto()  # `path.to.thing`
    TASK_CHECKBOX = auto()  # [ ] Task or [x] Task
    EVIDENCE_LINK = auto()  # 📎 claim
    AGENT_MENTION = auto()  # @agent
    CODE_FENCE = auto()  # ```lang ... ```
    ANNOTATION = auto()  # 💭 note


# === Token Patterns ===

# Order matters: more specific patterns first
TOKEN_PATTERNS: list[tuple[str, TokenType]] = [
    # Portal collapsed: ▶ [edge] ──→ summary OR ▶ [edge] summary
    # Use non-greedy matching and stop before another portal
    (r"▶\s*\[(\w+)\]\s*(?:──→\s*)?([^▶▼]+?)(?=\s*▶|\s*▼|$)", TokenType.PORTAL_COLLAPSED),
    # Portal expanded: ▼ [edge] ──→ summary OR ▼ [edge] summary OR ▼ [edge]
    # Content can follow with or without arrow
    (r"▼\s*\[(\w+)\](?:\s*(?:──→\s*)?([^▶▼]+?))?(?=\s*▶|\s*▼|$)", TokenType.PORTAL_EXPANDED),
    # Evidence link: 📎 claim (optional strength)
    (r"📎\s*(.+?)(?:\s*\((\w+)\))?$", TokenType.EVIDENCE_LINK),
    # Annotation: 💭 note
    (r"💭\s*(.+)", TokenType.ANNOTATION),
    # Agent mention: @agent
    (r"@(\w+)", TokenType.AGENT_MENTION),
    # Task checkbox: [ ] or [x] followed by text
    (r"\[([ xX])\]\s*(.+)", TokenType.TASK_CHECKBOX),
    # AGENTESE path: `world.foo.bar` or `self.context.manifest`
    (r"`((?:world|self|concept|void|time)(?:\.\w+)+)`", TokenType.AGENTESE_PATH),
    # Code fence start: ```lang
    (r"```(\w*)", TokenType.CODE_FENCE),
]

# Compile patterns for efficiency
COMPILED_PATTERNS: list[tuple[re.Pattern[str], TokenType]] = [
    (re.compile(pattern), token_type) for pattern, token_type in TOKEN_PATTERNS
]


# === Recognized Token ===


@dataclass
class RecognizedToken:
    """
    A token recognized in text.

    Contains the token type, matched groups, and position information.
    """

    token_type: TokenType
    raw_text: str  # The original matched text
    groups: tuple[str, ...]  # Captured groups from the pattern

    # Position in source text
    line: int = 0
    start_col: int = 0
    end_col: int = 0

    @property
    def edge_type(self) -> str | None:
        """For portal tokens, get the edge type."""
        if self.token_type in (TokenType.PORTAL_COLLAPSED, TokenType.PORTAL_EXPANDED):
            return self.groups[0] if self.groups else None
        return None

    @property
    def summary(self) -> str | None:
        """For portal tokens, get the summary."""
        if self.token_type == TokenType.PORTAL_COLLAPSED:
            return self.groups[1] if len(self.groups) > 1 else None
        if self.token_type == TokenType.PORTAL_EXPANDED:
            return self.groups[1] if len(self.groups) > 1 else None
        return None

    @property
    def path(self) -> str | None:
        """For AGENTESE path tokens, get the path."""
        if self.token_type == TokenType.AGENTESE_PATH:
            return self.groups[0] if self.groups else None
        return None

    @property
    def is_checked(self) -> bool | None:
        """For task checkboxes, check if checked."""
        if self.token_type == TokenType.TASK_CHECKBOX:
            return self.groups[0].lower() == "x" if self.groups else None
        return None

    @property
    def agent_name(self) -> str | None:
        """For agent mentions, get the agent name."""
        if self.token_type == TokenType.AGENT_MENTION:
            return self.groups[0] if self.groups else None
        return None

    @property
    def claim(self) -> str | None:
        """For evidence links, get the claim text."""
        if self.token_type == TokenType.EVIDENCE_LINK:
            return self.groups[0] if self.groups else None
        return None

    @property
    def evidence_strength(self) -> str | None:
        """For evidence links, get the strength if present."""
        if self.token_type == TokenType.EVIDENCE_LINK:
            return self.groups[1] if len(self.groups) > 1 else None
        return None


# === Parsing Functions ===


def extract_tokens(text: str) -> list[RecognizedToken]:
    """
    Extract all recognized tokens from text.

    Returns tokens in document order (line by line, left to right).

    Teaching:
        gotcha: This returns ALL tokens, including those inside code blocks.
                Use parse_text() for a structured parse that respects code fences.
                (Evidence: test_parser.py::test_extract_includes_code_block_contents)
    """
    tokens: list[RecognizedToken] = []

    lines = text.split("\n")
    for line_num, line in enumerate(lines):
        # Try each pattern
        for pattern, token_type in COMPILED_PATTERNS:
            for match in pattern.finditer(line):
                token = RecognizedToken(
                    token_type=token_type,
                    raw_text=match.group(0),
                    groups=match.groups(),
                    line=line_num,
                    start_col=match.start(),
                    end_col=match.end(),
                )
                tokens.append(token)

    # Sort by position (line, then column)
    tokens.sort(key=lambda t: (t.line, t.start_col))

    return tokens


@dataclass
class ParsedText:
    """
    Structured parse result.

    Contains the original text, extracted tokens, and metadata about
    code blocks and other structural elements.
    """

    text: str
    tokens: list[RecognizedToken]

    # Code block tracking
    code_blocks: list[tuple[int, int, str]] = field(
        default_factory=list
    )  # (start_line, end_line, lang)

    # Invisible metadata if present
    metadata: dict[str, Any] | None = None


def parse_text(text: str) -> ParsedText:
    """
    Parse text into a structured result.

    Unlike extract_tokens(), this respects code blocks and won't
    return tokens from inside fenced code.

    Teaching:
        gotcha: parse_text() strips invisible metadata from the text before
                tokenizing, then attaches it to the result.
                (Evidence: test_parser.py::test_parse_strips_metadata)
    """
    # Check for invisible metadata
    metadata = None
    clean_text = text
    if "\u200b" in text:  # Zero-width space marker
        clean_text, metadata = decode_invisible_metadata(text)

    # Find code blocks
    code_blocks: list[tuple[int, int, str]] = []
    lines = clean_text.split("\n")
    in_code_block = False
    code_start = 0
    code_lang = ""

    for i, line in enumerate(lines):
        if line.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_start = i
                code_lang = line[3:].strip()
            else:
                in_code_block = False
                code_blocks.append((code_start, i, code_lang))
                code_lang = ""

    # Extract tokens, filtering out those in code blocks
    all_tokens = extract_tokens(clean_text)

    def in_code_block_range(line: int) -> bool:
        for start, end, _ in code_blocks:
            if start < line < end:  # Exclude fence lines themselves
                return True
        return False

    tokens = [t for t in all_tokens if not in_code_block_range(t.line)]

    return ParsedText(
        text=clean_text,
        tokens=tokens,
        code_blocks=code_blocks,
        metadata=metadata,
    )


# === Invisible Metadata ===

# Zero-width space used as marker for invisible metadata
METADATA_MARKER = "\u200b"


def encode_invisible_metadata(
    visible_text: str,
    metadata: dict[str, Any],
) -> str:
    """
    Encode metadata invisibly into text.

    The metadata is base64-encoded JSON, prefixed with a zero-width space.
    It appears at the end of the text and is invisible to users.

    Teaching:
        gotcha: The encoded metadata WILL be copied when users copy text.
                This is intentional—it enables provenance tracking.
                (Evidence: test_parser.py::test_metadata_survives_copy)
    """
    # Serialize metadata to JSON
    json_str = json.dumps(metadata, default=str)  # default=str handles datetime

    # Base64 encode
    b64 = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

    # Append with marker
    return f"{visible_text}{METADATA_MARKER}{b64}"


def decode_invisible_metadata(
    text: str,
) -> tuple[str, dict[str, Any] | None]:
    """
    Decode invisible metadata from text.

    Returns (visible_text, metadata). If no metadata is present,
    returns (text, None).

    Teaching:
        gotcha: This is lenient—if decoding fails, it returns None for
                metadata rather than raising. Bad metadata shouldn't break paste.
                (Evidence: test_parser.py::test_decode_handles_corrupt_metadata)
    """
    if METADATA_MARKER not in text:
        return text, None

    parts = text.split(METADATA_MARKER, 1)
    if len(parts) != 2:
        return text, None

    visible_text = parts[0]
    b64_data = parts[1]

    try:
        json_str = base64.b64decode(b64_data).decode("utf-8")
        metadata = json.loads(json_str)
        return visible_text, metadata
    except (ValueError, json.JSONDecodeError):
        # Corrupted metadata—return original text
        return text, None


# === Convenience Functions ===


def is_portal_line(line: str) -> bool:
    """Check if a line is a portal (collapsed or expanded)."""
    return line.strip().startswith("▶") or line.strip().startswith("▼")


def is_agentese_path(text: str) -> bool:
    """Check if text is an AGENTESE path."""
    pattern = r"^(world|self|concept|void|time)(\.\w+)+$"
    return bool(re.match(pattern, text))


def extract_portal_info(line: str) -> tuple[bool, str, str] | None:
    """
    Extract portal information from a line.

    Returns (is_expanded, edge_type, summary) or None if not a portal.
    """
    tokens = extract_tokens(line)
    for token in tokens:
        if token.token_type == TokenType.PORTAL_COLLAPSED:
            return (False, token.edge_type or "", token.summary or "")
        if token.token_type == TokenType.PORTAL_EXPANDED:
            return (True, token.edge_type or "", token.summary or "")
    return None


__all__ = [
    # Token types
    "TokenType",
    "RecognizedToken",
    "ParsedText",
    # Parsing
    "extract_tokens",
    "parse_text",
    # Invisible metadata
    "encode_invisible_metadata",
    "decode_invisible_metadata",
    "METADATA_MARKER",
    # Convenience
    "is_portal_line",
    "is_agentese_path",
    "extract_portal_info",
]
