"""
Living Docs AGENTESE Nodes

Exposes Living Docs via AGENTESE paths:
- concept.docs: Documentation as projection
- self.docs: Docs for current file scope

See: spec/protocols/living-docs.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .extractor import DocstringExtractor
from .projector import LivingDocsProjector
from .types import DocNode, LivingDocsObserver, Tier

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer

logger = logging.getLogger(__name__)


# === concept.docs Node ===


@node(
    "concept.docs",
    description="Living Documentation - docs as projection",
    examples=[
        ("extract", {"path": "services/brain/persistence.py"}, "Extract DocNodes from file"),
        ("project", {"observer_kind": "agent"}, "Project docs for agent consumption"),
        ("list", {"tier": "rich"}, "List all RICH tier DocNodes"),
    ],
)
@dataclass
class LivingDocsNode(BaseLogosNode):
    """
    AGENTESE node for Living Documentation.

    The core functor: LivingDocs : (Source x Spec) -> Observer -> Surface

    Provides:
    - extract: Source -> DocNode
    - project: DocNode x Observer -> Surface
    - list: Filter and list DocNodes
    - gotchas: Get teaching moments from a file

    Teaching:
        gotcha: Observer kind must be one of: human, agent, ide.
                (Evidence: test_node.py::test_observer_validation)
    """

    _extractor: DocstringExtractor = field(default_factory=DocstringExtractor)
    _projector: LivingDocsProjector = field(default_factory=LivingDocsProjector)

    # Cache for extracted nodes per file
    _cache: dict[str, list[DocNode]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize mutable defaults."""
        # Ensure cache is initialized
        object.__setattr__(self, "_cache", {})

    @property
    def handle(self) -> str:
        return "concept.docs"

    # === Archetype Affordances ===

    _ARCHETYPE_AFFORDANCES: ClassVar[dict[str, tuple[str, ...]]] = {
        "developer": ("extract", "project", "list", "gotchas"),
        "architect": ("extract", "project", "list", "gotchas"),
        "reviewer": ("list", "gotchas"),
        "learner": ("list", "gotchas"),
        "guest": ("list",),
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        return self._ARCHETYPE_AFFORDANCES.get(archetype, ("list",))

    # === Aspect Hints ===

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "extract": "Extract DocNodes from a Python source file",
        "project": "Project docs for a specific observer kind (human/agent/ide)",
        "list": "List DocNodes with optional filtering by tier",
        "gotchas": "Get all teaching moments from a file",
    }

    # === Required Abstract Methods ===

    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Collapse to observer-appropriate representation."""
        return BasicRendering(
            summary="Living Docs - Documentation as Projection",
            content=(
                "Available aspects:\n"
                "- extract: Extract DocNodes from Python source\n"
                "- project: Project docs for observer (human/agent/ide)\n"
                "- list: List DocNodes with filtering\n"
                "- gotchas: Get teaching moments"
            ),
            metadata={"handle": self.handle},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to methods."""
        aspect_map: dict[str, Any] = {
            "extract": self.extract,
            "project": self.project,
            "list": self.list,
            "gotchas": self.gotchas,
        }

        handler = aspect_map.get(aspect)
        if handler is not None:
            return await handler(observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")

    # === Core Aspects ===

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Extract DocNodes from Python source",
    )
    async def extract(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str,
    ) -> Renderable:
        """
        Extract documentation from a source file.

        Args:
            observer: The observer context
            path: Path to Python file (absolute or relative to impl/claude)

        Returns:
            BasicRendering with extracted DocNodes
        """
        # Resolve path
        file_path = self._resolve_path(path)

        if not file_path.exists():
            return BasicRendering(
                summary=f"File not found: {path}",
                content="",
                metadata={"error": "not_found", "path": path},
            )

        if not file_path.suffix == ".py":
            return BasicRendering(
                summary=f"Not a Python file: {path}",
                content="",
                metadata={"error": "not_python", "path": path},
            )

        try:
            nodes = self._extractor.extract_file(file_path)
            # Cache for later use
            self._cache[str(file_path)] = nodes

            # Build summary
            tier_counts = {
                "minimal": sum(1 for n in nodes if n.tier == Tier.MINIMAL),
                "standard": sum(1 for n in nodes if n.tier == Tier.STANDARD),
                "rich": sum(1 for n in nodes if n.tier == Tier.RICH),
            }
            teaching_count = sum(len(n.teaching) for n in nodes)

            return BasicRendering(
                summary=f"Extracted {len(nodes)} DocNodes ({teaching_count} gotchas)",
                content="\n\n---\n\n".join(n.to_text() for n in nodes),
                metadata={
                    "node_count": len(nodes),
                    "tier_counts": tier_counts,
                    "teaching_count": teaching_count,
                    "nodes": [n.to_dict() for n in nodes],
                },
            )

        except SyntaxError as e:
            return BasicRendering(
                summary=f"Syntax error in {path}",
                content=str(e),
                metadata={"error": "syntax_error", "path": path},
            )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Project docs for specific observer",
    )
    async def project(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str,
        observer_kind: Literal["human", "agent", "ide"] = "human",
        density: Literal["compact", "comfortable", "spacious"] = "comfortable",
        symbol: str | None = None,
    ) -> Renderable:
        """
        Project documentation for a specific observer.

        Args:
            observer: The AGENTESE observer context
            path: Path to Python file
            observer_kind: Target observer type (human/agent/ide)
            density: Density level for human observers
            symbol: Optional specific symbol to project

        Returns:
            Projected Surface(s) wrapped in BasicRendering
        """
        # First extract if not cached
        file_path = self._resolve_path(path)
        cache_key = str(file_path)

        if cache_key not in self._cache:
            await self.extract(observer, path)

        nodes = self._cache.get(cache_key, [])

        if not nodes:
            return BasicRendering(
                summary="No DocNodes found",
                content="",
                metadata={"path": path},
            )

        # Filter by symbol if specified
        if symbol:
            nodes = [n for n in nodes if n.symbol == symbol]
            if not nodes:
                return BasicRendering(
                    summary=f"Symbol not found: {symbol}",
                    content="",
                    metadata={"path": path, "symbol": symbol},
                )

        # Create Living Docs observer
        docs_observer = LivingDocsObserver(kind=observer_kind, density=density)

        # Project all nodes
        surfaces = self._projector.project_many(nodes, docs_observer)

        # Combine surfaces
        combined_content = "\n\n---\n\n".join(s.content for s in surfaces)

        return BasicRendering(
            summary=f"Projected {len(surfaces)} docs for {observer_kind}",
            content=combined_content,
            metadata={
                "observer_kind": observer_kind,
                "density": density,
                "format": surfaces[0].format if surfaces else "unknown",
                "surfaces": [s.to_dict() for s in surfaces],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="List DocNodes with filtering",
    )
    async def list(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str | None = None,
        tier: Literal["minimal", "standard", "rich"] | None = None,
        only_with_teaching: bool = False,
    ) -> Renderable:
        """
        List DocNodes with optional filtering.

        Args:
            observer: The observer context
            path: Optional path to filter by
            tier: Minimum tier to include
            only_with_teaching: Only include nodes with teaching moments

        Returns:
            List of matching DocNodes
        """
        # Gather nodes from cache or extract
        all_nodes: list[DocNode] = []

        if path:
            file_path = self._resolve_path(path)
            cache_key = str(file_path)
            if cache_key not in self._cache:
                await self.extract(observer, path)
            all_nodes = self._cache.get(cache_key, [])
        else:
            # Return all cached nodes
            for nodes in self._cache.values():
                all_nodes.extend(nodes)

        # Apply filters
        if tier:
            tier_enum = Tier(tier)
            tier_order = [Tier.MINIMAL, Tier.STANDARD, Tier.RICH]
            min_tier_idx = tier_order.index(tier_enum)
            all_nodes = [n for n in all_nodes if tier_order.index(n.tier) >= min_tier_idx]

        if only_with_teaching:
            all_nodes = [n for n in all_nodes if n.teaching]

        # Build summary
        symbols = [n.symbol for n in all_nodes]

        return BasicRendering(
            summary=f"Found {len(all_nodes)} DocNodes",
            content="\n".join(f"- {n.symbol} ({n.tier.value})" for n in all_nodes),
            metadata={
                "count": len(all_nodes),
                "symbols": symbols,
                "nodes": [n.to_dict() for n in all_nodes],
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Get teaching moments from a file",
    )
    async def gotchas(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str,
        severity: Literal["info", "warning", "critical"] | None = None,
    ) -> Renderable:
        """
        Get all teaching moments (gotchas) from a file.

        Args:
            observer: The observer context
            path: Path to Python file
            severity: Optional severity filter

        Returns:
            List of teaching moments with provenance
        """
        # Extract if not cached
        file_path = self._resolve_path(path)
        cache_key = str(file_path)

        if cache_key not in self._cache:
            await self.extract(observer, path)

        nodes = self._cache.get(cache_key, [])

        # Gather all teaching moments
        moments: list[tuple[str, Any]] = []  # (symbol, TeachingMoment)
        for node in nodes:
            for moment in node.teaching:
                if severity is None or moment.severity == severity:
                    moments.append((node.symbol, moment))

        if not moments:
            return BasicRendering(
                summary="No teaching moments found",
                content="",
                metadata={"path": path},
            )

        # Format moments
        lines: list[str] = []
        for symbol, moment in moments:
            severity_icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(
                moment.severity, "•"
            )
            lines.append(f"{severity_icon} **{symbol}**: {moment.insight}")
            if moment.evidence:
                lines.append(f"   Evidence: `{moment.evidence}`")

        return BasicRendering(
            summary=f"Found {len(moments)} gotchas",
            content="\n".join(lines),
            metadata={
                "count": len(moments),
                "moments": [{"symbol": sym, **m.to_dict()} for sym, m in moments],
            },
        )

    # === Helpers ===

    def _resolve_path(self, path: str) -> Path:
        """Resolve a path relative to impl/claude if needed."""
        p = Path(path)
        if p.is_absolute():
            return p

        # Try relative to impl/claude
        impl_claude = Path(__file__).parent.parent.parent
        candidate = impl_claude / path
        if candidate.exists():
            return candidate

        # Fall back to current directory
        return Path.cwd() / path


# === self.docs Node ===


@node(
    "self.docs",
    description="Docs for current file scope",
    examples=[
        ("for_file", {"path": "current_file.py"}, "Get docs for current file"),
        ("gotchas", {}, "Teaching moments in current scope"),
    ],
)
@dataclass
class SelfDocsNode(BaseLogosNode):
    """
    self.docs - documentation in current scope.

    A scoped view of Living Docs for the file/module you're working in.
    """

    _parent: LivingDocsNode = field(default_factory=LivingDocsNode)

    @property
    def handle(self) -> str:
        return "self.docs"

    _ARCHETYPE_AFFORDANCES: ClassVar[dict[str, tuple[str, ...]]] = {
        "developer": ("for_file", "gotchas"),
        "architect": ("for_file", "gotchas"),
        "reviewer": ("gotchas",),
        "learner": ("gotchas",),
        "guest": (),
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return self._ARCHETYPE_AFFORDANCES.get(archetype, ())

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "for_file": "Get documentation for a specific file",
        "gotchas": "Get teaching moments in the current scope",
    }

    # === Required Abstract Methods ===

    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
    ) -> Renderable:
        """Collapse to observer-appropriate representation."""
        return BasicRendering(
            summary="self.docs - Docs for Current Scope",
            content=(
                "Available aspects:\n"
                "- for_file: Get docs for a specific file\n"
                "- gotchas: Get teaching moments in scope"
            ),
            metadata={"handle": self.handle},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to methods."""
        aspect_map: dict[str, Any] = {
            "for_file": self.for_file,
            "gotchas": self.gotchas,
        }

        handler = aspect_map.get(aspect)
        if handler is not None:
            return await handler(observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")

    # === Core Aspects ===

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Get docs for current file",
    )
    async def for_file(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str,
        observer_kind: Literal["human", "agent", "ide"] = "human",
        density: Literal["compact", "comfortable", "spacious"] = "comfortable",
    ) -> Renderable:
        """
        Get documentation for a specific file.

        Convenience wrapper around concept.docs.project.
        """
        return await self._parent.project(
            observer,
            path=path,
            observer_kind=observer_kind,
            density=density,
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="Teaching moments in scope",
    )
    async def gotchas(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        path: str | None = None,
        scope: str | None = None,
    ) -> Renderable:
        """
        Get teaching moments in the current scope.

        Args:
            observer: The observer context
            path: Optional file path
            scope: Optional scope filter (module or class name)

        Returns:
            Teaching moments in scope
        """
        if path is None:
            return BasicRendering(
                summary="No path specified",
                content="Provide a path to get gotchas from",
                metadata={},
            )

        result = await self._parent.gotchas(observer, path=path)

        # Filter by scope if specified
        # We know _parent.gotchas returns BasicRendering
        if scope and isinstance(result, BasicRendering):
            moments = result.metadata.get("moments", [])
            if moments:
                filtered = [m for m in moments if scope.lower() in m.get("symbol", "").lower()]
                return BasicRendering(
                    summary=f"Found {len(filtered)} gotchas in scope '{scope}'",
                    content=result.content,
                    metadata={"count": len(filtered), "moments": filtered},
                )

        return result


# === Factory Functions ===


def get_living_docs_node() -> LivingDocsNode:
    """Get a LivingDocsNode instance."""
    return LivingDocsNode()


def get_self_docs_node() -> SelfDocsNode:
    """Get a SelfDocsNode instance."""
    return SelfDocsNode()


# === Exports ===

__all__ = [
    "LivingDocsNode",
    "SelfDocsNode",
    "get_living_docs_node",
    "get_self_docs_node",
]
