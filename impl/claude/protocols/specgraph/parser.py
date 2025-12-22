"""
SpecGraph Parser: Discover edges and tokens from markdown content.

This module parses spec markdown to discover:
- Edges: References to other specs, implementations, tests
- Tokens: Interactive elements (AGENTESE paths, code blocks, etc.)

The parser is the first step in building the SpecGraph—it transforms
static markdown into a navigable hypergraph.

Design Principle:
    "Edges are discovered, not declared."

The parser uses regex patterns to find:
1. AGENTESE paths: `self.memory.crystallize`
2. Implementation refs: `impl/claude/...`
3. Test refs: `_tests/...` or `tests/...`
4. Heritage citations: **Heritage Citation**
5. See also refs: **See**: `spec/...`
6. AD references: (AD-001), (AD-002)
7. Code blocks: ```python ... ```
8. Type references: `PolyAgent[S, A, B]`

Teaching:
    gotcha: Patterns are applied line-by-line for line numbers.
            Multi-line patterns (code blocks) are handled specially.

    gotcha: Edge discovery is heuristic—not all references are edges.
            The parser errs on the side of discovery; pruning comes later.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .types import (
    EdgeType,
    SpecEdge,
    SpecNode,
    SpecTier,
    SpecToken,
    TokenType,
    spec_path_to_agentese,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Regex Patterns
# =============================================================================

# AGENTESE paths: `world.something`, `self.memory.crystallize`, etc.
AGENTESE_PATH_PATTERN = re.compile(r"`((?:world|self|concept|void|time)\.[a-z][a-z0-9_.]*)`")

# Implementation references: `impl/claude/...`
IMPL_REF_PATTERN = re.compile(r"`(impl/claude/[^`]+)`")

# Test references: `_tests/...` or `tests/...`
TEST_REF_PATTERN = re.compile(r"`(_tests/[^`]+|tests/[^`]+)`")

# Spec references: `spec/...`
SPEC_REF_PATTERN = re.compile(r"`(spec/[^`]+\.md)`")

# Heritage citations: **Heritage Citation...**: ...
HERITAGE_PATTERN = re.compile(r"\*\*Heritage Citation[^:]*\*\*:\s*([^\n]+)")

# See/Related references: **See**: `...`
SEE_ALSO_PATTERN = re.compile(r"\*\*See\*\*:?\s*`([^`]+)`")

# AD references: (AD-001), (AD-002), etc.
AD_REF_PATTERN = re.compile(r"\(AD-(\d+)\)")

# Principle references: (Tasteful), (Composable), etc.
PRINCIPLE_PATTERN = re.compile(
    r"\((Tasteful|Curated|Ethical|Joy-Inducing|Composable|Heterarchical|Generative)\)"
)

# Type references: CapitalizedWord[...] or CapitalizedWord
TYPE_REF_PATTERN = re.compile(r"`([A-Z][a-zA-Z]+(?:\[[^\]]+\])?)`")

# arXiv references: arXiv:1234.5678
ARXIV_PATTERN = re.compile(r"arXiv:(\d+\.\d+)")

# Code blocks: ```language ... ```
CODE_BLOCK_START = re.compile(r"^```(\w*)$")
CODE_BLOCK_END = re.compile(r"^```$")

# Title extraction: # Title
TITLE_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


# =============================================================================
# Parser Result
# =============================================================================


@dataclass
class ParseResult:
    """Result of parsing a spec file."""

    node: SpecNode
    edges: list[SpecEdge]
    tokens: list[SpecToken]

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def token_count(self) -> int:
        return len(self.tokens)


# =============================================================================
# Parser
# =============================================================================


class SpecParser:
    """
    Parser for spec markdown files.

    Discovers edges and tokens from markdown content.
    Each spec becomes a SpecNode with associated edges and tokens.
    """

    def __init__(self, repo_root: Path | None = None):
        """
        Initialize parser.

        Args:
            repo_root: Root of the repository for resolving paths.
                      Defaults to current working directory.
        """
        self.repo_root = repo_root or Path.cwd()

    def parse_file(self, spec_path: str | Path) -> ParseResult:
        """
        Parse a spec file and discover edges/tokens.

        Args:
            spec_path: Path to the spec file (relative to repo root)

        Returns:
            ParseResult with node, edges, and tokens
        """
        path = Path(spec_path)
        full_path = self.repo_root / path if not path.is_absolute() else path

        # Read content
        content = full_path.read_text(encoding="utf-8")

        # Create node
        node = self._create_node(str(path), content)

        # Discover edges and tokens
        edges = self._discover_edges(str(path), content)
        tokens = self._discover_tokens(str(path), content)

        return ParseResult(node=node, edges=edges, tokens=tokens)

    def parse_content(self, spec_path: str, content: str) -> ParseResult:
        """
        Parse spec content directly (for testing or in-memory specs).

        Args:
            spec_path: The path this content would have
            content: The markdown content

        Returns:
            ParseResult with node, edges, and tokens
        """
        node = self._create_node(spec_path, content)
        edges = self._discover_edges(spec_path, content)
        tokens = self._discover_tokens(spec_path, content)

        return ParseResult(node=node, edges=edges, tokens=tokens)

    def _create_node(self, spec_path: str, content: str) -> SpecNode:
        """Create a SpecNode from parsed content."""
        # Extract title
        title_match = TITLE_PATTERN.search(content)
        title = title_match.group(1) if title_match else Path(spec_path).stem

        # Determine tier
        tier = self._infer_tier(spec_path)

        # Create AGENTESE path
        agentese_path = spec_path_to_agentese(spec_path)

        # Find derives_from from extends edges
        derives_from = self._find_derives_from(content)

        return SpecNode(
            path=spec_path,
            agentese_path=agentese_path,
            title=title,
            tier=tier,
            derives_from=derives_from,
            confidence=0.5,  # Default; updated by derivation framework
            _content=content,
        )

    def _infer_tier(self, spec_path: str) -> SpecTier:
        """Infer the tier from the spec path."""
        path = Path(spec_path)
        parts = path.parts

        if "spec" not in parts:
            return SpecTier.APPLICATION

        # Bootstrap specs
        bootstrap_names = {
            "principles.md",
            "bootstrap.md",
            "composition.md",
            "primitives.md",
            "anatomy.md",
        }
        if path.name in bootstrap_names:
            return SpecTier.BOOTSTRAP

        # Protocol specs
        if "protocols" in parts:
            return SpecTier.PROTOCOL

        # Agent specs (any -gent directory)
        for part in parts:
            if part.endswith("-gent") or part.endswith("-gents") or part == "agents":
                return SpecTier.AGENT

        # Service specs
        if "services" in parts:
            return SpecTier.SERVICE

        return SpecTier.APPLICATION

    def _find_derives_from(self, content: str) -> tuple[str, ...]:
        """Find spec dependencies from content."""
        derives = []

        # Look for "extends" or "See" references
        for match in SEE_ALSO_PATTERN.finditer(content):
            ref = match.group(1)
            if ref.startswith("spec/") and ref.endswith(".md"):
                derives.append(ref)

        # Look for explicit spec references
        for match in SPEC_REF_PATTERN.finditer(content):
            ref = match.group(1)
            if ref not in derives:
                derives.append(ref)

        return tuple(derives)

    def _discover_edges(self, spec_path: str, content: str) -> list[SpecEdge]:
        """Discover all edges from the spec content."""
        edges: list[SpecEdge] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # AGENTESE paths → references
            for match in AGENTESE_PATH_PATTERN.finditer(line):
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.REFERENCES,
                        source=spec_path,
                        target=match.group(1),
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

            # Implementation references → implements
            for match in IMPL_REF_PATTERN.finditer(line):
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.IMPLEMENTS,
                        source=spec_path,
                        target=match.group(1),
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

            # Test references → tests
            for match in TEST_REF_PATTERN.finditer(line):
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.TESTS,
                        source=spec_path,
                        target=match.group(1),
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

            # Spec references → extends
            for match in SPEC_REF_PATTERN.finditer(line):
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.EXTENDS,
                        source=spec_path,
                        target=match.group(1),
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

            # Heritage citations
            heritage_match = HERITAGE_PATTERN.search(line)
            if heritage_match:
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.HERITAGE,
                        source=spec_path,
                        target=heritage_match.group(1)[:100],  # Truncate long citations
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

            # arXiv references
            for match in ARXIV_PATTERN.finditer(line):
                edges.append(
                    SpecEdge(
                        edge_type=EdgeType.HERITAGE,
                        source=spec_path,
                        target=f"arXiv:{match.group(1)}",
                        context=line.strip(),
                        line_number=line_num,
                    )
                )

        return edges

    def _discover_tokens(self, spec_path: str, content: str) -> list[SpecToken]:
        """Discover all interactive tokens from the spec content."""
        tokens: list[SpecToken] = []
        lines = content.split("\n")

        in_code_block = False
        code_block_start_line = 0
        code_block_lang = ""
        code_block_content: list[str] = []

        for line_num, line in enumerate(lines, start=1):
            # Handle code blocks
            if not in_code_block:
                start_match = CODE_BLOCK_START.match(line)
                if start_match:
                    in_code_block = True
                    code_block_start_line = line_num
                    code_block_lang = start_match.group(1) or "text"
                    code_block_content = []
                    continue
            else:
                if CODE_BLOCK_END.match(line):
                    # End of code block
                    tokens.append(
                        SpecToken(
                            token_type=TokenType.CODE_BLOCK,
                            content="\n".join(code_block_content),
                            line_number=code_block_start_line,
                            column=0,
                            context=f"```{code_block_lang}",
                        )
                    )
                    in_code_block = False
                    continue
                else:
                    code_block_content.append(line)
                    continue

            # Skip non-code-block processing while in code block
            if in_code_block:
                continue

            # AGENTESE paths
            for match in AGENTESE_PATH_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.AGENTESE_PATH,
                        content=match.group(1),
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

            # AD references
            for match in AD_REF_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.AD_REFERENCE,
                        content=f"AD-{match.group(1)}",
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

            # Principle references
            for match in PRINCIPLE_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.PRINCIPLE_REF,
                        content=match.group(1),
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

            # Implementation references
            for match in IMPL_REF_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.IMPL_REF,
                        content=match.group(1),
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

            # Test references
            for match in TEST_REF_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.TEST_REF,
                        content=match.group(1),
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

            # Type references (skip if looks like a file path)
            for match in TYPE_REF_PATTERN.finditer(line):
                ref = match.group(1)
                # Skip if it's clearly a path
                if "/" not in ref and not ref.endswith(".py"):
                    tokens.append(
                        SpecToken(
                            token_type=TokenType.TYPE_REF,
                            content=ref,
                            line_number=line_num,
                            column=match.start(),
                            context=line.strip(),
                        )
                    )

            # Heritage references (arXiv)
            for match in ARXIV_PATTERN.finditer(line):
                tokens.append(
                    SpecToken(
                        token_type=TokenType.HERITAGE_REF,
                        content=f"arXiv:{match.group(1)}",
                        line_number=line_num,
                        column=match.start(),
                        context=line.strip(),
                    )
                )

        return tokens


# =============================================================================
# Convenience Functions
# =============================================================================


def parse_spec(spec_path: str | Path, repo_root: Path | None = None) -> ParseResult:
    """
    Parse a spec file.

    Convenience function that creates a parser and parses the file.
    """
    parser = SpecParser(repo_root=repo_root)
    return parser.parse_file(spec_path)


def parse_spec_content(spec_path: str, content: str) -> ParseResult:
    """
    Parse spec content directly.

    Convenience function for testing or in-memory specs.
    """
    parser = SpecParser()
    return parser.parse_content(spec_path, content)


__all__ = [
    "SpecParser",
    "ParseResult",
    "parse_spec",
    "parse_spec_content",
]
