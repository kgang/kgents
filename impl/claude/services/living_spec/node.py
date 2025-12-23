"""
SpecNode: Unified hypergraph node with token affordances.

The SpecNode is the core unification of the Living Spec system. It combines:
- ContextNode hypergraph navigation (from typed-hypergraph)
- Interactive token extraction (from interactive-text)
- Portal expansion (from portal-token)

A SpecNode is both:
1. A node in the typed-hypergraph (with observer-dependent edges)
2. A container of interactive tokens (with observer-dependent affordances)

Philosophy:
    "The file is a lie. The lens is a lie. There is only the typed-hypergraph."
    "The text is not passive—it is interface."
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .contracts import (
    Affordance,
    Observer,
    ObserverRole,
    SpecKind,
)
from .tokens import PortalSpecToken, PortalState, SpecToken
from .tokens.base import (
    AGENTESEPathToken,
    CodeBlockToken,
    ImageToken,
    PrincipleRefToken,
    RequirementRefToken,
    TaskCheckboxToken,
)

if TYPE_CHECKING:
    from .monad import SpecMonad


# -----------------------------------------------------------------------------
# Hyperedge Types
# -----------------------------------------------------------------------------

# Standard hyperedge types (from typed-hypergraph spec)
STRUCTURAL_EDGES = frozenset(
    {"contains", "contained_in", "parent", "imports", "imported_by", "calls", "called_by"}
)
TESTING_EDGES = frozenset({"tests", "tested_by", "covers", "covered_by"})
SPECIFICATION_EDGES = frozenset({"implements", "implemented_by", "derives_from", "derived_by"})
EVIDENCE_EDGES = frozenset(
    {"evidence", "evidences", "supports", "supported_by", "refutes", "refuted_by"}
)
TEMPORAL_EDGES = frozenset({"evolved_from", "evolved_to", "supersedes", "superseded_by"})
SEMANTIC_EDGES = frozenset({"related", "similar", "contrasts"})

ALL_EDGE_TYPES = (
    STRUCTURAL_EDGES
    | TESTING_EDGES
    | SPECIFICATION_EDGES
    | EVIDENCE_EDGES
    | TEMPORAL_EDGES
    | SEMANTIC_EDGES
)

# Observer-dependent edge visibility
EDGE_VISIBILITY: dict[ObserverRole, frozenset[str]] = {
    ObserverRole.DEVELOPER: frozenset(
        {"tests", "imports", "calls", "implements", "contains", "parent"}
    ),
    ObserverRole.ARCHITECT: frozenset(
        {"imports", "calls", "contains", "parent", "derives_from", "related"}
    ),
    ObserverRole.SECURITY_AUDITOR: frozenset(
        {"imports", "calls", "evidence", "supports", "refutes"}
    ),
    ObserverRole.NEWCOMER: frozenset({"contains", "parent", "related", "similar"}),
}


# -----------------------------------------------------------------------------
# Token Extraction Patterns
# -----------------------------------------------------------------------------

# Regex patterns for token extraction
AGENTESE_PATTERN = re.compile(r"`((?:world|self|concept|void|time)\.[a-z_.]+)`")
TASK_PATTERN = re.compile(r"^- \[([ xX])\] (.+)$", re.MULTILINE)
CODE_BLOCK_PATTERN = re.compile(r"```(\w*)\n([\s\S]*?)```")
IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
PRINCIPLE_PATTERN = re.compile(
    r"\(AD-\d+\)|\((Tasteful|Curated|Ethical|Joy-Inducing|Composable|Heterarchical|Generative)\)"
)
REQUIREMENT_PATTERN = re.compile(r"_Requirements:\s*([\d.,\s]+)_")


# -----------------------------------------------------------------------------
# SpecNode
# -----------------------------------------------------------------------------


@dataclass
class SpecNode:
    """
    A node in the living spec hypergraph.

    Combines hypergraph navigation (edges to related nodes) with
    interactive tokens (affordances for user interaction).

    Key properties:
    - Lazy loading: content and tokens load only on access
    - Observer-dependent: edges and affordances vary by observer
    - Portal-aware: can expand edges inline as portal tokens
    """

    path: str  # AGENTESE path or file path
    kind: SpecKind = SpecKind.SPEC

    # Lazy-loaded content
    _content: str | None = field(default=None, repr=False)
    _tokens: list[SpecToken] | None = field(default=None, repr=False)

    # Cached edges (computed on first access)
    _edges_cache: dict[str, list["SpecNode"]] | None = field(default=None, repr=False)

    # Metadata
    _metadata: dict[str, Any] = field(default_factory=dict)

    # -------------------------------------------------------------------------
    # Content Access (Lazy)
    # -------------------------------------------------------------------------

    async def content(self) -> str:
        """
        Get node content (lazy-loaded).

        Returns:
            Content string (markdown for specs, code for implementations)
        """
        if self._content is None:
            self._content = await self._load_content()
        return self._content

    async def _load_content(self) -> str:
        """Load content from file system."""
        # Convert AGENTESE path to file path if needed
        file_path = self._resolve_path()

        if file_path and file_path.exists():
            return file_path.read_text()

        return ""

    def _resolve_path(self) -> Path | None:
        """Resolve AGENTESE path or file path to filesystem Path."""
        # If already a file path
        if "/" in self.path or self.path.endswith(".md") or self.path.endswith(".py"):
            return Path(self.path)

        # AGENTESE path resolution
        # world.brain → impl/claude/services/brain/
        # concept.specgraph → spec/protocols/specgraph.md
        parts = self.path.split(".")
        if not parts:
            return None

        context = parts[0]
        rest = parts[1:] if len(parts) > 1 else []

        if context == "world":
            # world.X → impl/claude/services/X/
            base = Path("impl/claude/services")
            if rest:
                return base / "/".join(rest)
        elif context == "concept":
            # concept.X → spec/protocols/X.md or spec/agents/X.md
            if rest:
                spec_path = Path("spec/protocols") / f"{rest[-1]}.md"
                if spec_path.exists():
                    return spec_path
                agent_path = Path("spec/agents") / f"{rest[-1]}.md"
                if agent_path.exists():
                    return agent_path
        elif context == "self":
            # self.X → impl/claude/services/X/
            base = Path("impl/claude/services")
            if rest:
                return base / "/".join(rest)

        return None

    # -------------------------------------------------------------------------
    # Token Extraction (Lazy)
    # -------------------------------------------------------------------------

    async def tokens(self) -> list[SpecToken]:
        """
        Extract interactive tokens from content (lazy-loaded).

        Returns:
            List of SpecToken instances found in content
        """
        if self._tokens is None:
            content = await self.content()
            self._tokens = self._extract_tokens(content)
        return self._tokens

    def _extract_tokens(self, content: str) -> list[SpecToken]:
        """Extract all token types from content."""
        tokens: list[SpecToken] = []

        # AGENTESE paths
        for match in AGENTESE_PATTERN.finditer(content):
            tokens.append(
                AGENTESEPathToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                )
            )

        # Task checkboxes
        for match in TASK_PATTERN.finditer(content):
            tokens.append(
                TaskCheckboxToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                )
            )

        # Code blocks
        for match in CODE_BLOCK_PATTERN.finditer(content):
            tokens.append(
                CodeBlockToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                    _metadata={"language": match.group(1)},
                )
            )

        # Images
        for match in IMAGE_PATTERN.finditer(content):
            tokens.append(
                ImageToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                    _metadata={"alt": match.group(1), "src": match.group(2)},
                )
            )

        # Principle references
        for match in PRINCIPLE_PATTERN.finditer(content):
            tokens.append(
                PrincipleRefToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                )
            )

        # Requirement references
        for match in REQUIREMENT_PATTERN.finditer(content):
            tokens.append(
                RequirementRefToken(
                    _span=(match.start(), match.end()),
                    _value=match.group(0),
                )
            )

        # Sort by span start
        tokens.sort(key=lambda t: t.span[0])
        return tokens

    # -------------------------------------------------------------------------
    # Hypergraph Navigation
    # -------------------------------------------------------------------------

    def edges(self, observer: Observer) -> dict[str, list["SpecNode"]]:
        """
        Get observer-dependent hyperedges.

        Different observers see different edges:
        - Developer: tests, imports, calls, implements
        - Architect: dependencies, patterns, violations
        - Security auditor: auth_flows, data_flows, vulnerabilities
        - Newcomer: docs, examples, related

        Returns:
            Dict mapping edge type → list of destination nodes
        """
        if self._edges_cache is None:
            self._edges_cache = self._resolve_edges()

        # Filter by observer visibility
        visible_types = EDGE_VISIBILITY.get(observer.role, frozenset())
        return {k: v for k, v in self._edges_cache.items() if k in visible_types}

    def _resolve_edges(self) -> dict[str, list["SpecNode"]]:
        """Resolve all hyperedges (not yet filtered by observer)."""
        edges: dict[str, list[SpecNode]] = {}

        file_path = self._resolve_path()
        if not file_path:
            return edges

        # Tests edge
        test_files = self._find_test_files(file_path)
        if test_files:
            edges["tests"] = [SpecNode(path=str(f), kind=SpecKind.TEST) for f in test_files]

        # Implements edge (for implementation files)
        if self.kind == SpecKind.IMPLEMENTATION:
            spec_files = self._find_spec_files(file_path)
            if spec_files:
                edges["implements"] = [
                    SpecNode(path=str(f), kind=SpecKind.SPEC) for f in spec_files
                ]

        # Contains edge (for directories)
        if file_path.is_dir():
            children = list(file_path.iterdir())
            edges["contains"] = [
                SpecNode(path=str(f), kind=self._infer_kind(f))
                for f in children
                if not f.name.startswith("_") and not f.name.startswith(".")
            ]

        # Parent edge
        if file_path.parent.exists():
            edges["parent"] = [SpecNode(path=str(file_path.parent))]

        return edges

    def _find_test_files(self, file_path: Path) -> list[Path]:
        """Find test files for a given file."""
        if not file_path.exists():
            return []

        tests_dir = file_path.parent / "_tests"
        if tests_dir.exists():
            name = file_path.stem
            return list(tests_dir.glob(f"test_{name}*.py"))
        return []

    def _find_spec_files(self, file_path: Path) -> list[Path]:
        """Find spec files that this file implements."""
        # Look for spec files with similar names
        name = file_path.stem
        spec_patterns = [
            Path("spec/protocols") / f"{name}.md",
            Path("spec/agents") / f"{name}.md",
            Path("spec/services") / f"{name}.md",
        ]
        return [p for p in spec_patterns if p.exists()]

    def _infer_kind(self, path: Path) -> SpecKind:
        """Infer SpecKind from file path."""
        path_str = str(path)
        if "_tests" in path_str or path.name.startswith("test_"):
            return SpecKind.TEST
        elif "spec/" in path_str:
            return SpecKind.SPEC
        elif "impl/" in path_str:
            return SpecKind.IMPLEMENTATION
        return SpecKind.SPEC

    # -------------------------------------------------------------------------
    # Portal Creation
    # -------------------------------------------------------------------------

    def as_portal(
        self, edge_type: str, observer: Observer, depth: int = 0
    ) -> PortalSpecToken | None:
        """
        Create a portal token for a specific edge type.

        Args:
            edge_type: Type of hyperedge (tests, implements, etc.)
            observer: Current observer (for visibility check)
            depth: Nesting depth

        Returns:
            PortalSpecToken if edge exists and is visible, else None
        """
        edges = self.edges(observer)
        if edge_type not in edges:
            return None

        destinations = [node.path for node in edges[edge_type]]
        return PortalSpecToken.create(
            edge_type=edge_type,
            destinations=destinations,
            depth=depth,
            content_loader=self._load_destination_content,
        )

    async def _load_destination_content(self, path: str) -> str:
        """Load content for a portal destination."""
        node = SpecNode(path=path)
        return await node.content()

    # -------------------------------------------------------------------------
    # Affordances
    # -------------------------------------------------------------------------

    def affordances(self, observer: Observer) -> list[Affordance]:
        """
        Get all affordances from tokens.

        Returns:
            List of affordances (filtered by observer capabilities)
        """
        if self._tokens is None:
            return []

        affordances = []
        for token in self._tokens:
            aff = token.affordance(observer)
            if aff is not None:
                affordances.append(aff)
        return affordances

    # -------------------------------------------------------------------------
    # Monad Entry
    # -------------------------------------------------------------------------

    def enter_monad(self) -> "SpecMonad":
        """
        Enter editing monad for this spec.

        Returns:
            SpecMonad with this node as the spec being edited
        """
        from .monad import SpecMonad

        return SpecMonad.pure(self)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        return {
            "path": self.path,
            "kind": self.kind.value,
            "has_content": self._content is not None,
            "token_count": len(self._tokens) if self._tokens else 0,
            "metadata": self._metadata,
        }

    async def to_manifest(self, observer: Observer) -> dict[str, Any]:
        """
        Full manifest including content, tokens, and edges.

        This is the complete representation for display.
        """
        content = await self.content()
        tokens = await self.tokens()
        edges = self.edges(observer)

        return {
            "path": self.path,
            "kind": self.kind.value,
            "content": content,
            "tokens": [t.to_dict() for t in tokens],
            "edges": {k: [n.path for n in v] for k, v in edges.items()},
            "affordances": [a.__dict__ for a in self.affordances(observer)],
            "metadata": self._metadata,
        }

    def __repr__(self) -> str:
        return f"SpecNode(path={self.path!r}, kind={self.kind.name})"
