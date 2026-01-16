"""
Constitution AGENTESE Node: @node("self.constitution")

Exposes the Constitutional K-Blocks via AGENTESE for self-reflective navigation.

AGENTESE Paths:
- self.constitution.manifest      - Constitutional graph overview
- self.constitution.view          - View the Constitutional graph (with optional layer filter)
- self.constitution.navigate      - Navigate derivation chain from a K-Block
- self.constitution.axioms        - Get L0 axiom K-Blocks (A1, A2, A3, G)
- self.constitution.principles    - Get L1-L2 principle K-Blocks
- self.constitution.architecture  - Get L3 architecture K-Blocks
- self.constitution.inspect       - Deep inspect a specific K-Block

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "The Constitution is not documentation - it is executable architecture."
    "The compiler that knows itself is the compiler that trusts itself."

See: docs/skills/metaphysical-fullstack.md
See: plans/self-reflective-os/
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .models import (
    DerivationChain as CodebaseDerivationChain,
    KBlockGraph,
    KBlockInspection as CodebaseKBlockInspection,
)
from .reflection_service import (
    ConstitutionalGraph,
    DerivationChain,
    KBlockInspection,
    SelfReflectionService,
    get_reflection_service,
)
from .scanner import CodebaseScanner

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


# =============================================================================
# Renderings
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalGraphRendering:
    """Rendering for the Constitutional graph."""

    graph: ConstitutionalGraph

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "constitutional_graph",
            **self.graph.to_dict(),
        }

    def to_text(self) -> str:
        return self.graph.to_text()


@dataclass(frozen=True)
class DerivationChainRendering:
    """Rendering for a derivation chain."""

    chain: DerivationChain

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "derivation_chain",
            **self.chain.to_dict(),
        }

    def to_text(self) -> str:
        return self.chain.to_text()


@dataclass(frozen=True)
class KBlockListRendering:
    """Rendering for a list of K-Blocks."""

    kblocks: list[dict[str, Any]]
    layer_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kblock_list",
            "layer_name": self.layer_name,
            "count": len(self.kblocks),
            "kblocks": self.kblocks,
        }

    def to_text(self) -> str:
        lines = [f"{self.layer_name} K-Blocks ({len(self.kblocks)})", "=" * 40, ""]
        for kb in self.kblocks:
            lines.append(f"- {kb['id']}: {kb['title']}")
            lines.append(f"  Layer: L{kb['layer']}, Loss: {kb['galois_loss']:.3f}")
            lines.append("")
        return "\n".join(lines)


@dataclass(frozen=True)
class KBlockInspectionRendering:
    """Rendering for a K-Block inspection."""

    inspection: KBlockInspection

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "kblock_inspection",
            **self.inspection.to_dict(),
        }

    def to_text(self) -> str:
        return self.inspection.to_text()


# =============================================================================
# ConstitutionNode
# =============================================================================


@node(
    "self.constitution",
    description="Constitutional Foundation - Navigate and inspect the 22 K-Blocks",
    dependencies=("reflection_service",),
    contracts={
        # Perception aspects
        "manifest": Response(ConstitutionalGraph),
        "view": Response(ConstitutionalGraph),
        "axioms": Response(list),
        "principles": Response(list),
        "architecture": Response(list),
        # Navigation aspects
        "navigate": Response(DerivationChain),
        "inspect": Response(KBlockInspection),
    },
    examples=[
        ("view", {}, "View the Constitutional graph"),
        ("view", {"layer": "axioms"}, "View L0 axioms only"),
        ("axioms", {}, "Get the 4 foundational axioms"),
        ("principles", {}, "Get Constitution + 7 principles"),
        ("architecture", {}, "Get L3 architecture K-Blocks"),
        ("navigate", {"kblock_id": "ASHC"}, "Trace ASHC derivation to axioms"),
        ("inspect", {"kblock_id": "A3_MIRROR"}, "Deep inspect the Mirror axiom"),
    ],
    constitutional=True,  # This node IS the Constitution - evaluate itself!
)
class ConstitutionNode(BaseLogosNode):
    """
    AGENTESE node for Constitutional self-reflection.

    Exposes the 22 Constitutional K-Blocks through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    The Self-Reflective OS Pattern:
    - The Constitution is not documentation - it is executable architecture
    - Every K-Block is navigable, inspectable, and derivable
    - Galois loss tracks coherence from axioms to implementation

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/constitution/axioms

        # Via Logos directly
        await logos.invoke("self.constitution.view", observer)

        # Via CLI
        kg constitution view --layer axioms
    """

    def __init__(
        self,
        reflection_service: SelfReflectionService | None = None,
    ) -> None:
        """
        Initialize ConstitutionNode.

        Args:
            reflection_service: The reflection service (injected by container)
                              If None, creates a default instance.
        """
        self._service = reflection_service or get_reflection_service()

    @property
    def handle(self) -> str:
        return "self.constitution"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        The Constitution is universally readable - all archetypes can
        view and navigate. This embodies the Constitutional principle
        of transparency.
        """
        # All archetypes get full read access to the Constitution
        # This is intentional - the Constitution should be transparent
        return (
            "view",
            "navigate",
            "axioms",
            "principles",
            "architecture",
            "inspect",
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View the Constitutional graph overview",
        examples=["self.constitution.manifest", "self.constitution.view"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Manifest the Constitutional graph to observer.

        AGENTESE: self.constitution.manifest
        """
        graph = await self._service.get_constitution()
        return ConstitutionalGraphRendering(graph=graph)

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View the Constitutional graph with optional layer filter",
        examples=[
            "self.constitution.view",
            "self.constitution.view[layer=axioms]",
            "self.constitution.view[layer=0]",
        ],
    )
    async def view(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        layer: str | int | None = None,
        **kwargs: Any,
    ) -> ConstitutionalGraph:
        """
        View the Constitutional graph.

        Args:
            layer: Optional layer filter (0-3 or "axioms", "kernel", "derived",
                   "principles", "architecture")

        Returns:
            ConstitutionalGraph with all K-Blocks and edges
        """
        return await self._service.get_constitution(layer=layer)

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Navigate derivation chain from a K-Block to axioms",
        examples=[
            "self.constitution.navigate[kblock_id=ASHC]",
            "self.constitution.navigate[kblock_id=COMPOSABLE]",
        ],
    )
    async def navigate(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        kblock_id: str = "",
        **kwargs: Any,
    ) -> DerivationChain:
        """
        Navigate the derivation chain from a K-Block back to axioms.

        Args:
            kblock_id: The K-Block ID to trace (e.g., "ASHC", "COMPOSABLE")

        Returns:
            DerivationChain showing the path to axioms
        """
        if not kblock_id:
            # Default to CONSTITUTION if no ID provided
            kblock_id = "CONSTITUTION"
        return await self._service.get_derivation_chain(kblock_id)

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get the L0 axiom K-Blocks (A1, A2, A3, G)",
        examples=["self.constitution.axioms"],
    )
    async def axioms(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get all L0 axiom K-Blocks.

        Returns:
            List of axiom K-Blocks (A1_ENTITY, A2_MORPHISM, A3_MIRROR, G_GALOIS)
        """
        blocks = await self._service.get_axioms()
        return [
            {
                "id": b.id,
                "title": b.title,
                "layer": b.layer,
                "galois_loss": b.galois_loss,
                "derives_from": list(b.derives_from),
                "tags": list(b.tags),
            }
            for b in blocks
        ]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get the Constitution and 7 principle K-Blocks",
        examples=["self.constitution.principles"],
    )
    async def principles(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get the Constitution and all 7 principle K-Blocks.

        Returns:
            List of principle K-Blocks (CONSTITUTION, TASTEFUL, CURATED, etc.)
        """
        blocks = await self._service.get_principles()
        return [
            {
                "id": b.id,
                "title": b.title,
                "layer": b.layer,
                "galois_loss": b.galois_loss,
                "derives_from": list(b.derives_from),
                "tags": list(b.tags),
            }
            for b in blocks
        ]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get the L3 architecture K-Blocks",
        examples=["self.constitution.architecture"],
    )
    async def architecture(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get all L3 architecture K-Blocks.

        Returns:
            List of architecture K-Blocks (ASHC, METAPHYSICAL_FULLSTACK, etc.)
        """
        blocks = await self._service.get_architecture()
        return [
            {
                "id": b.id,
                "title": b.title,
                "layer": b.layer,
                "galois_loss": b.galois_loss,
                "derives_from": list(b.derives_from),
                "tags": list(b.tags),
            }
            for b in blocks
        ]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Deep inspect a specific K-Block",
        examples=[
            "self.constitution.inspect[kblock_id=A3_MIRROR]",
            "self.constitution.inspect[kblock_id=COMPOSABLE]",
        ],
    )
    async def inspect(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        kblock_id: str = "",
        **kwargs: Any,
    ) -> KBlockInspection:
        """
        Deep inspect a K-Block with full content and relationships.

        Args:
            kblock_id: The K-Block ID to inspect (e.g., "A3_MIRROR", "COMPOSABLE")

        Returns:
            KBlockInspection with full content, parents, children, and derivation chain
        """
        if not kblock_id:
            kblock_id = "CONSTITUTION"
        return await self._service.inspect(kblock_id)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "view":
            graph = await self.view(observer, **kwargs)
            return ConstitutionalGraphRendering(graph=graph).to_dict()

        elif aspect == "navigate":
            chain = await self.navigate(observer, **kwargs)
            return DerivationChainRendering(chain=chain).to_dict()

        elif aspect == "axioms":
            kblocks = await self.axioms(observer, **kwargs)
            return KBlockListRendering(kblocks=kblocks, layer_name="L0 Axioms").to_dict()

        elif aspect == "principles":
            kblocks = await self.principles(observer, **kwargs)
            return KBlockListRendering(kblocks=kblocks, layer_name="L1-L2 Principles").to_dict()

        elif aspect == "architecture":
            kblocks = await self.architecture(observer, **kwargs)
            return KBlockListRendering(kblocks=kblocks, layer_name="L3 Architecture").to_dict()

        elif aspect == "inspect":
            inspection = await self.inspect(observer, **kwargs)
            return KBlockInspectionRendering(inspection=inspection).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# DriftNode - Spec/Impl Coherence Monitoring
# =============================================================================


@dataclass(frozen=True)
class DriftReportRendering:
    """Rendering for a drift report."""

    report: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "drift_report",
            **self.report,
        }

    def to_text(self) -> str:
        lines = [
            "Drift Report",
            "=" * 40,
            f"Health Status: {self.report.get('health_status', 'unknown')}",
            f"Overall Coherence: {self.report.get('overall_coherence', 0):.1%}",
            f"Drift Percentage: {self.report.get('drift_percentage', 0):.1f}%",
            f"Total K-Blocks: {self.report.get('total_kblocks', 0)}",
            f"Grounded K-Blocks: {self.report.get('grounded_kblocks', 0)}",
            f"Orphan K-Blocks: {len(self.report.get('orphan_kblocks', []))}",
            f"Divergences: {len(self.report.get('spec_impl_divergences', []))}",
            "",
            "Principle Coverage:",
        ]
        for principle, coverage in self.report.get("principle_coverage", {}).items():
            bar = "█" * int(coverage * 20) + "░" * (20 - int(coverage * 20))
            lines.append(f"  {principle}: [{bar}] {coverage:.0%}")
        return "\n".join(lines)


@dataclass(frozen=True)
class OrphanListRendering:
    """Rendering for list of orphan K-Blocks."""

    orphans: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "orphan_list",
            "count": len(self.orphans),
            "orphan_ids": self.orphans,
        }

    def to_text(self) -> str:
        if not self.orphans:
            return "No orphan K-Blocks found. All K-Blocks are grounded."
        lines = [
            f"Orphan K-Blocks ({len(self.orphans)})",
            "=" * 40,
            "",
            "These K-Blocks have no derivation root to L1 axioms:",
            "",
        ]
        for orphan_id in self.orphans[:20]:  # Show first 20
            lines.append(f"  - {orphan_id}")
        if len(self.orphans) > 20:
            lines.append(f"  ... and {len(self.orphans) - 20} more")
        return "\n".join(lines)


@dataclass(frozen=True)
class CoverageRendering:
    """Rendering for principle coverage."""

    coverage: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "principle_coverage",
            "coverage": self.coverage,
        }

    def to_text(self) -> str:
        lines = [
            "Principle Coverage",
            "=" * 40,
            "",
        ]
        for principle, score in sorted(self.coverage.items(), key=lambda x: -x[1]):
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {principle}: [{bar}] {score:.0%}")
        return "\n".join(lines)


@node(
    "self.drift",
    description="Drift Detection - Monitor spec/impl coherence",
    dependencies=("reflection_service",),
    contracts={
        # Perception aspects
        "report": Response(dict),
        "orphans": Response(list),
        "coverage": Response(dict),
    },
    examples=[
        ("report", {}, "Get comprehensive drift report"),
        ("orphans", {}, "List K-Blocks without derivation roots"),
        ("coverage", {}, "Get principle coverage scores"),
    ],
)
class DriftNode(BaseLogosNode):
    """
    AGENTESE node for Drift Detection.

    Monitors spec/impl coherence by tracking:
    - Orphan K-Blocks (no derivation to axioms)
    - High Galois loss (semantic drift)
    - Principle coverage (which principles are represented)

    Philosophy:
        "The system illuminates, not enforces. Drift is not failure—
         it's the natural cost of creating. What matters is knowing."

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/drift/report

        # Via Logos directly
        await logos.invoke("self.drift.report", observer)

        # Via CLI
        kg drift report
    """

    def __init__(
        self,
        reflection_service: SelfReflectionService | None = None,
    ) -> None:
        """
        Initialize DriftNode.

        Args:
            reflection_service: The reflection service (injected by container)
                              If None, creates a default instance.
        """
        self._service = reflection_service or get_reflection_service()

    @property
    def handle(self) -> str:
        return "self.drift"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Drift detection is readable by all archetypes to support
        transparency and self-reflection.
        """
        return ("report", "orphans", "coverage")

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get comprehensive drift analysis report",
        examples=["self.drift.report", "self.drift.manifest"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        Manifest drift report to observer.

        AGENTESE: self.drift.manifest
        """
        report = await self._service.get_drift_report()
        return DriftReportRendering(report=report.to_dict())

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get comprehensive drift analysis report",
        examples=["self.drift.report"],
    )
    async def report(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get comprehensive drift analysis report.

        Returns:
            DriftReport with spec/impl divergence analysis
        """
        report = await self._service.get_drift_report()
        return report.to_dict()

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="List K-Blocks without derivation roots",
        examples=["self.drift.orphans"],
    )
    async def orphans(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[str]:
        """
        Get list of orphaned K-Block IDs.

        Returns:
            List of K-Block IDs without derivation to L1 axioms
        """
        return await self._service.get_orphans()

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get principle coverage scores",
        examples=["self.drift.coverage"],
    )
    async def coverage(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, float]:
        """
        Get principle coverage scores.

        Returns:
            Dictionary mapping principle name to coverage score (0.0 - 1.0)
        """
        return await self._service.compute_principle_coverage()

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "report":
            report = await self.report(observer, **kwargs)
            return DriftReportRendering(report=report).to_dict()

        elif aspect == "orphans":
            orphans = await self.orphans(observer, **kwargs)
            return OrphanListRendering(orphans=orphans).to_dict()

        elif aspect == "coverage":
            coverage = await self.coverage(observer, **kwargs)
            return CoverageRendering(coverage=coverage).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# CodebaseNode Contracts and Renderings
# =============================================================================


@dataclass(frozen=True)
class GraphRequest:
    """Request for generating codebase graph."""

    path: str = "services"  # Relative to project root


@dataclass(frozen=True)
class GraphResponse:
    """Response containing K-Block graph."""

    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    root_path: str
    stats: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "root_path": self.root_path,
            "stats": self.stats,
        }


@dataclass(frozen=True)
class InspectRequest:
    """Request for inspecting a file."""

    file_path: str


@dataclass(frozen=True)
class InspectResponse:
    """Response containing K-Block inspection."""

    kblock: dict[str, Any]
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    source_lines: int
    complexity_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "kblock": self.kblock,
            "classes": self.classes,
            "functions": self.functions,
            "source_lines": self.source_lines,
            "complexity_score": self.complexity_score,
        }


@dataclass(frozen=True)
class DeriveRequest:
    """Request for tracing derivation chain."""

    file_path: str
    max_depth: int = 10


@dataclass(frozen=True)
class DeriveResponse:
    """Response containing derivation chain."""

    target_id: str
    target_path: str
    chain: list[dict[str, Any]]
    depth: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_path": self.target_path,
            "chain": self.chain,
            "depth": self.depth,
        }


@dataclass(frozen=True)
class CodebaseManifestResponse:
    """Response for codebase manifest."""

    project_root: str
    scanned: bool
    cached_modules: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": self.project_root,
            "scanned": self.scanned,
            "cached_modules": self.cached_modules,
        }


@dataclass(frozen=True)
class CodebaseManifestRendering:
    """Rendering for codebase manifest."""

    response: CodebaseManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        return (
            f"Codebase Scanner\n"
            f"================\n"
            f"Project Root: {self.response.project_root}\n"
            f"Cached Modules: {self.response.cached_modules}"
        )


@dataclass(frozen=True)
class GraphRendering:
    """Rendering for K-Block graph."""

    graph: KBlockGraph

    def to_dict(self) -> dict[str, Any]:
        return self.graph.to_dict()

    def to_text(self) -> str:
        stats = self.graph.to_dict()["stats"]
        return (
            f"K-Block Graph: {self.graph.root_path}\n"
            f"================\n"
            f"Nodes: {stats['node_count']}\n"
            f"Edges: {stats['edge_count']}\n"
            f"Avg Galois Loss: {stats['avg_galois_loss']:.3f}"
        )


@dataclass(frozen=True)
class CodebaseInspectionRendering:
    """Rendering for K-Block inspection."""

    inspection: CodebaseKBlockInspection

    def to_dict(self) -> dict[str, Any]:
        return self.inspection.to_dict()

    def to_text(self) -> str:
        kb = self.inspection.kblock
        lines = [
            f"Module: {kb.path}",
            f"ID: {kb.id}",
            f"Lines: {self.inspection.source_lines}",
            f"Complexity: {self.inspection.complexity_score:.1f}",
            f"Galois Loss: {kb.galois_loss:.3f}",
            "",
        ]
        if kb.docstring:
            lines.append(f"Docstring: {kb.docstring[:100]}...")
        lines.append("")
        lines.append(f"Classes ({len(self.inspection.classes)}):")
        for cls in self.inspection.classes[:5]:
            lines.append(f"  - {cls.name}: {len(cls.methods)} methods")
        lines.append("")
        lines.append(f"Functions ({len(self.inspection.functions)}):")
        for fn in self.inspection.functions[:5]:
            async_str = "async " if fn.is_async else ""
            lines.append(f"  - {async_str}{fn.name}({', '.join(fn.parameters[:3])})")
        return "\n".join(lines)


@dataclass(frozen=True)
class CodebaseDerivationRendering:
    """Rendering for derivation chain."""

    chain: CodebaseDerivationChain

    def to_dict(self) -> dict[str, Any]:
        return self.chain.to_dict()

    def to_text(self) -> str:
        lines = [
            f"Derivation Chain: {self.chain.target_path}",
            f"Depth: {self.chain.depth}",
            "",
        ]
        for node_id, edge_type, context in self.chain.chain[:10]:
            lines.append(f"  <- [{edge_type}] {node_id[:20]}... ({context or 'no context'})")
        if len(self.chain.chain) > 10:
            lines.append(f"  ... and {len(self.chain.chain) - 10} more")
        return "\n".join(lines)


# =============================================================================
# CodebaseNode
# =============================================================================


@node(
    "self.codebase",
    description="Codebase Scanner - K-Block representations of Python modules",
    dependencies=("codebase_scanner",),
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(CodebaseManifestResponse),
        # Query/mutation aspects (Contract with request + response)
        "graph": Contract(GraphRequest, GraphResponse),
        "inspect": Contract(InspectRequest, InspectResponse),
        "derive": Contract(DeriveRequest, DeriveResponse),
    },
    examples=[
        ("graph", {"path": "services"}, "Scan services directory"),
        ("inspect", {"file_path": "services/brain/__init__.py"}, "Inspect brain module"),
        ("derive", {"file_path": "services/witness/persistence.py"}, "Trace dependencies"),
    ],
)
class CodebaseNode(BaseLogosNode):
    """
    AGENTESE node for Codebase Scanner.

    Exposes CodebaseScanner through the universal protocol.
    Enables the Self-Reflective OS pattern where the system
    can understand and navigate its own structure.

    Example:
        # Via AGENTESE gateway
        POST /agentese/self/codebase/graph
        {"path": "services"}

        # Via Logos directly
        await logos.invoke("self.codebase.graph", observer, path="services")

        # Via CLI
        kgents codebase graph services

    Teaching:
        gotcha: CodebaseNode REQUIRES codebase_scanner dependency. Without it,
                instantiation fails with TypeError.

        gotcha: Paths are relative to the project root configured in the scanner.
                Use absolute paths or ensure project_root is set correctly.

        gotcha: Graph generation can be slow for large codebases. Consider
                caching or limiting scope with path parameter.
    """

    def __init__(self, codebase_scanner: CodebaseScanner) -> None:
        """
        Initialize CodebaseNode.

        Args:
            codebase_scanner: The scanner instance (injected by container)

        Raises:
            TypeError: If codebase_scanner is not provided
        """
        self._scanner = codebase_scanner

    @property
    def handle(self) -> str:
        return "self.codebase"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        All archetypes can read codebase structure.
        Only developers can derive (intensive operation).
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Base affordances for all
        base = ("graph", "inspect")

        # Developers get derive (can be intensive)
        if archetype_lower in ("developer", "operator", "admin", "system", "architect"):
            return base + ("derive",)

        return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest codebase scanner status to observer.

        AGENTESE: self.codebase.manifest
        """
        if self._scanner is None:
            return BasicRendering(
                summary="Codebase scanner not initialized",
                content="No scanner configured",
                metadata={"error": "no_scanner"},
            )

        response = CodebaseManifestResponse(
            project_root=str(self._scanner.project_root),
            scanned=len(self._scanner._module_cache) > 0,
            cached_modules=len(self._scanner._module_cache),
        )
        return CodebaseManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to scanner methods.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if self._scanner is None:
            return {"error": "Codebase scanner not configured"}

        if aspect == "graph":
            return await self._handle_graph(kwargs)
        elif aspect == "inspect":
            return await self._handle_inspect(kwargs)
        elif aspect == "derive":
            return await self._handle_derive(kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_graph(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle graph aspect - scan directory and return K-Block graph."""
        path_str = kwargs.get("path", "services")
        path = Path(path_str)

        try:
            graph = await self._scanner.scan_to_graph(path)
            return GraphRendering(graph=graph).to_dict()
        except FileNotFoundError as e:
            return {"error": f"Directory not found: {e}"}
        except Exception as e:
            logger.error(f"Error scanning {path}: {e}")
            return {"error": str(e)}

    async def _handle_inspect(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle inspect aspect - deep inspect a single file."""
        file_path_str = kwargs.get("file_path") or kwargs.get("path")
        if not file_path_str:
            return {"error": "file_path required"}

        file_path = Path(file_path_str)

        try:
            inspection = await self._scanner.inspect_module(file_path)
            return CodebaseInspectionRendering(inspection=inspection).to_dict()
        except FileNotFoundError as e:
            return {"error": f"File not found: {e}"}
        except SyntaxError as e:
            return {"error": f"Syntax error in file: {e}"}
        except Exception as e:
            logger.error(f"Error inspecting {file_path}: {e}")
            return {"error": str(e)}

    async def _handle_derive(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle derive aspect - trace derivation chain."""
        file_path_str = kwargs.get("file_path") or kwargs.get("path")
        if not file_path_str:
            return {"error": "file_path required"}

        file_path = Path(file_path_str)
        max_depth = kwargs.get("max_depth", 10)

        try:
            chain = await self._scanner.derive_chain(file_path, max_depth=max_depth)
            return CodebaseDerivationRendering(chain=chain).to_dict()
        except Exception as e:
            logger.error(f"Error deriving chain for {file_path}: {e}")
            return {"error": str(e)}


# =============================================================================
# WitnessTimelineNode - Aggregated Timeline of Witness Activity
# =============================================================================


@dataclass(frozen=True)
class TimelineRendering:
    """Rendering for timeline events."""

    events: list[dict[str, Any]]
    total: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "timeline",
            "events": self.events,
            "total": self.total,
        }

    def to_text(self) -> str:
        lines = [
            f"Witness Timeline ({self.total} events)",
            "=" * 40,
            "",
        ]
        for event in self.events[:20]:
            ts = event.get("timestamp", "?")[:19]
            summary = event.get("summary", "")[:50]
            event_type = event.get("event_type", "?")
            lines.append(f"[{ts}] ({event_type}) {summary}")
        if len(self.events) > 20:
            lines.append(f"... and {len(self.events) - 20} more events")
        return "\n".join(lines)


@dataclass(frozen=True)
class ActivityRendering:
    """Rendering for development activity summary."""

    activity: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "development_activity",
            **self.activity,
        }

    def to_text(self) -> str:
        lines = [
            f"Development Activity ({self.activity.get('period', 'unknown')})",
            "=" * 40,
            f"Period: {self.activity.get('start_date', '?')[:10]} to {self.activity.get('end_date', '?')[:10]}",
            f"Total Marks: {self.activity.get('total_marks', 0)}",
            f"Total Crystals: {self.activity.get('total_crystals', 0)}",
            f"Total Decisions: {self.activity.get('total_decisions', 0)}",
            "",
            "By Actor:",
        ]
        for actor, count in self.activity.get("events_by_actor", {}).items():
            lines.append(f"  {actor}: {count}")
        lines.append("")
        lines.append("Top Files:")
        for file, count in self.activity.get("top_files", [])[:5]:
            lines.append(f"  {file}: {count}")
        return "\n".join(lines)


@dataclass(frozen=True)
class MarkSearchRendering:
    """Rendering for mark search results."""

    marks: list[dict[str, Any]]
    query: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "mark_search",
            "query": self.query,
            "count": len(self.marks),
            "marks": self.marks,
        }

    def to_text(self) -> str:
        lines = [
            f"Mark Search: '{self.query}' ({len(self.marks)} results)",
            "=" * 40,
            "",
        ]
        for mark in self.marks[:20]:
            mark_id = mark.get("id", "?")[:16]
            origin = mark.get("origin", "?")
            tags = ", ".join(mark.get("tags", [])[:3])
            lines.append(f"[{mark_id}] ({origin}) tags: {tags}")
        if len(self.marks) > 20:
            lines.append(f"... and {len(self.marks) - 20} more")
        return "\n".join(lines)


@node(
    "self.timeline",
    description="Development Timeline - View all witness activity (marks, crystals, decisions)",
    dependencies=("witness_timeline_service",),
    contracts={
        "view": Response(list),
        "search": Response(list),
        "for_file": Response(list),
        "activity": Response(dict),
    },
    examples=[
        ("view", {}, "Get recent witness timeline"),
        ("view", {"limit": 50}, "Get last 50 timeline events"),
        ("search", {"query": "refactoring"}, "Search marks for 'refactoring'"),
        ("for_file", {"path": "services/witness/mark.py"}, "Get witnesses for a file"),
        ("activity", {"period": "week"}, "Get weekly development activity"),
    ],
)
class WitnessTimelineNode(BaseLogosNode):
    """
    AGENTESE node for Development Timeline.

    Provides unified access to all witness activity:
    - Marks (execution artifacts)
    - Crystals (compressed memory)
    - Decisions (dialectical fusions)

    Philosophy:
        "The timeline is the heartbeat. Every action leaves a mark.
         Every mark joins the stream. Every stream tells a story."

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/timeline/view

        # Via Logos directly
        await logos.invoke("self.timeline.view", observer)

        # Via CLI
        kg timeline view --limit 50
    """

    def __init__(
        self,
        witness_timeline_service: Any | None = None,
    ) -> None:
        """
        Initialize WitnessTimelineNode.

        Args:
            witness_timeline_service: The timeline service (injected by container)
        """
        self._service = witness_timeline_service

    def _get_service(self) -> Any:
        """Lazy-load service if not injected."""
        if self._service is None:
            from .witness_timeline_service import get_witness_timeline_service

            self._service = get_witness_timeline_service()
        return self._service

    @property
    def handle(self) -> str:
        return "self.timeline"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can read timeline data."""
        return ("view", "search", "for_file", "activity")

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get aggregated development timeline",
        examples=["self.timeline.view", "self.timeline.view[limit=50]"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest development timeline to observer."""
        events = await self.view(observer, **kwargs)
        return TimelineRendering(events=events, total=len(events))

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="View aggregated development timeline with optional filters",
        examples=[
            "self.timeline.view",
            "self.timeline.view[limit=50]",
            "self.timeline.view[event_types=mark,crystal]",
        ],
    )
    async def view(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        limit: int = 100,
        offset: int = 0,
        event_types: str | None = None,
        actor: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get aggregated timeline of all witness activity.

        Args:
            limit: Maximum events to return (default 100)
            offset: Number of events to skip
            event_types: Comma-separated event types (mark,crystal,decision)
            actor: Filter by actor (kent, claude, system)

        Returns:
            List of timeline events as dictionaries
        """
        from .witness_timeline_service import ActorType, EventType, TimelineFilter

        # Build filter
        filter_args: dict[str, Any] = {}

        if event_types:
            types = [EventType(t.strip()) for t in event_types.split(",")]
            filter_args["event_types"] = tuple(types)

        if actor:
            filter_args["actors"] = (ActorType(actor),)

        timeline_filter = TimelineFilter(**filter_args) if filter_args else None

        service = self._get_service()
        events = await service.get_timeline(filter=timeline_filter, limit=limit, offset=offset)
        return [e.to_dict() for e in events]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Search marks by text query",
        examples=["self.timeline.search[query=refactoring]"],
    )
    async def search(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        query: str = "",
        limit: int = 50,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Search marks by text query.

        Args:
            query: Search query string
            limit: Maximum results (default 50)

        Returns:
            List of matching marks
        """
        if not query:
            return []
        service = self._get_service()
        return await service.search_marks(query, limit=limit)  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get witnesses related to a file",
        examples=["self.timeline.for_file[path=services/witness/mark.py]"],
    )
    async def for_file(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        path: str = "",
        limit: int = 50,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get witness marks related to a specific file.

        Args:
            path: File path to search for
            limit: Maximum results (default 50)

        Returns:
            List of related marks
        """
        if not path:
            return []
        service = self._get_service()
        return await service.get_marks_for_file(path, limit=limit)  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get development activity summary",
        examples=["self.timeline.activity", "self.timeline.activity[period=week]"],
    )
    async def activity(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        period: str = "week",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get development activity summary.

        Args:
            period: Time period ('day', 'week', 'month')

        Returns:
            Development activity statistics
        """
        service = self._get_service()
        activity = await service.get_development_activity(period=period)
        return activity.to_dict()  # type: ignore[no-any-return]

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate methods."""
        if aspect == "view":
            events = await self.view(observer, **kwargs)
            return TimelineRendering(events=events, total=len(events)).to_dict()

        elif aspect == "search":
            marks = await self.search(observer, **kwargs)
            query = kwargs.get("query", "")
            return MarkSearchRendering(marks=marks, query=query).to_dict()

        elif aspect == "for_file":
            marks = await self.for_file(observer, **kwargs)
            return {"type": "file_witnesses", "path": kwargs.get("path", ""), "marks": marks}

        elif aspect == "activity":
            activity = await self.activity(observer, **kwargs)
            return ActivityRendering(activity=activity).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# InspectionNode - Universal Inspection for System Elements
# =============================================================================


@dataclass(frozen=True)
class InspectionRendering:
    """Rendering for inspection result."""

    result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "inspection",
            **self.result,
        }

    def to_text(self) -> str:
        lines = [
            f"Inspection: {self.result.get('path', '?')}",
            "=" * 60,
            f"K-Block ID: {self.result.get('kblock_id', '?')}",
            f"Layer: L{self.result.get('layer', '?')} ({self.result.get('layer_name', '?')})",
            f"Drift Status: {self.result.get('drift_status', 'unknown')}",
            "",
            "Summary:",
            self.result.get("content_summary", "")[:500],
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class QuickInspectionRendering:
    """Rendering for quick inspection result."""

    result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "quick_inspection",
            **self.result,
        }

    def to_text(self) -> str:
        return (
            f"{self.result.get('kind', '?')}: {self.result.get('identifier', '?')} - "
            f"{self.result.get('summary', '')[:60]}"
        )


@node(
    "self.inspect",
    description="Universal Inspection - Deep inspect any system element",
    dependencies=("inspection_service",),
    contracts={
        "file": Response(dict),
        "kblock": Response(dict),
        "quick": Response(dict),
    },
    examples=[
        ("file", {"path": "services/witness/mark.py"}, "Inspect a file"),
        ("kblock", {"kblock_id": "COMPOSABLE"}, "Inspect a K-Block"),
        ("quick", {"identifier": "ASHC"}, "Quick inspection"),
    ],
)
class InspectionNode(BaseLogosNode):
    """
    AGENTESE node for Universal Inspection.

    Provides deep inspection of any system element:
    - Files (Python modules, specs, plans)
    - K-Blocks (Constitutional and codebase)
    - Marks and Crystals

    Philosophy:
        "Inspection is introspection. The system that sees itself can trust itself."

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/inspect/file?path=services/witness/mark.py

        # Via Logos directly
        await logos.invoke("self.inspect.kblock", observer, kblock_id="COMPOSABLE")

        # Via CLI
        kg inspect file services/witness/mark.py
    """

    def __init__(
        self,
        inspection_service: Any | None = None,
    ) -> None:
        """
        Initialize InspectionNode.

        Args:
            inspection_service: The inspection service (injected by container)
        """
        self._service = inspection_service

    def _get_service(self) -> Any:
        """Lazy-load service if not injected."""
        if self._service is None:
            from .inspection_service import get_inspection_service

            self._service = get_inspection_service()
        return self._service

    @property
    def handle(self) -> str:
        return "self.inspect"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can inspect."""
        return ("file", "kblock", "quick")

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Inspect any element (auto-detects type)",
        examples=["self.inspect.manifest[identifier=ASHC]"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        identifier: str = "",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest inspection result to observer."""
        if not identifier:
            return BasicRendering(
                summary="Inspection requires an identifier",
                content="Provide a file path, K-Block ID, or mark ID",
                metadata={"error": "missing_identifier"},
            )
        result = await self._get_service().inspect(identifier)
        return InspectionRendering(result=result.to_dict())

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Inspect a file with full context",
        examples=["self.inspect.file[path=services/witness/mark.py]"],
    )
    async def file(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        path: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Inspect a file with full context.

        Args:
            path: File path (absolute or relative to project root)

        Returns:
            InspectionResult with file analysis
        """
        if not path:
            return {"error": "path required"}
        service = self._get_service()
        result = await service.inspect_file(path)
        return result.to_dict()  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Inspect a K-Block with derivation chain",
        examples=["self.inspect.kblock[kblock_id=COMPOSABLE]"],
    )
    async def kblock(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        kblock_id: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Inspect a K-Block with derivation chain.

        Args:
            kblock_id: K-Block identifier (e.g., "COMPOSABLE", "ASHC")

        Returns:
            InspectionResult with K-Block details
        """
        if not kblock_id:
            return {"error": "kblock_id required"}
        service = self._get_service()
        result = await service.inspect_kblock(kblock_id)
        return result.to_dict()  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Lightweight inspection for quick lookups",
        examples=["self.inspect.quick[identifier=ASHC]"],
    )
    async def quick(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        identifier: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Lightweight inspection for quick lookups.

        Args:
            identifier: File path, K-Block ID, or mark ID

        Returns:
            QuickInspection with basic information
        """
        if not identifier:
            return {"error": "identifier required"}
        service = self._get_service()
        result = await service.quick_inspect(identifier)
        return result.to_dict()  # type: ignore[no-any-return]

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate methods."""
        if aspect == "file":
            result = await self.file(observer, **kwargs)
            return InspectionRendering(result=result).to_dict()

        elif aspect == "kblock":
            result = await self.kblock(observer, **kwargs)
            return InspectionRendering(result=result).to_dict()

        elif aspect == "quick":
            result = await self.quick(observer, **kwargs)
            return QuickInspectionRendering(result=result).to_dict()

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# GitNode - Git History Integration
# =============================================================================


@dataclass(frozen=True)
class CommitListRendering:
    """Rendering for list of commits."""

    commits: list[dict[str, Any]]
    total: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "commit_list",
            "commits": self.commits,
            "total": self.total,
        }

    def to_text(self) -> str:
        lines = [
            f"Git History ({self.total} commits)",
            "=" * 60,
            "",
        ]
        for commit in self.commits[:20]:
            sha = commit.get("short_sha", "?")
            author = commit.get("author", "?")
            date = commit.get("date", "?")[:10]
            msg = commit.get("message", "")[:50]
            lines.append(f"[{sha}] {date} ({author}) {msg}")
        if len(self.commits) > 20:
            lines.append(f"... and {len(self.commits) - 20} more")
        return "\n".join(lines)


@dataclass(frozen=True)
class FileHistoryRendering:
    """Rendering for file history."""

    history: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "file_history",
            **self.history,
        }

    def to_text(self) -> str:
        path = self.history.get("path", "?")
        commits = self.history.get("commits", [])
        lines = [
            f"File History: {path}",
            "=" * 60,
            f"Total commits: {self.history.get('total_commits', len(commits))}",
            "",
        ]
        for commit in commits[:10]:
            sha = commit.get("short_sha", "?")
            msg = commit.get("message", "")[:40]
            lines.append(f"  [{sha}] {msg}")
        return "\n".join(lines)


@dataclass(frozen=True)
class BlameRendering:
    """Rendering for git blame."""

    blame: list[dict[str, Any]]
    path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "blame",
            "path": self.path,
            "lines": self.blame,
        }

    def to_text(self) -> str:
        lines = [
            f"Git Blame: {self.path}",
            "=" * 60,
            "",
        ]
        for bl in self.blame[:30]:
            ln = bl.get("line_number", 0)
            sha = bl.get("short_sha", "?")
            author = bl.get("author", "?")[:10]
            content = bl.get("content", "")[:40]
            lines.append(f"{ln:4d} [{sha}] {author:10s} | {content}")
        if len(self.blame) > 30:
            lines.append(f"... and {len(self.blame) - 30} more lines")
        return "\n".join(lines)


@node(
    "self.git",
    description="Git History - Access repository history, blame, and diffs",
    dependencies=("git_service",),
    contracts={
        "history": Response(list),
        "file_history": Response(dict),
        "blame": Response(list),
        "diff": Response(str),
        "search": Response(list),
        "spec_impl": Response(list),
    },
    examples=[
        ("history", {}, "Get recent commits"),
        ("history", {"limit": 20}, "Get last 20 commits"),
        ("file_history", {"path": "services/self/node.py"}, "Get history for a file"),
        ("blame", {"path": "services/self/node.py"}, "Get blame for a file"),
        ("diff", {"sha": "abc123"}, "Get diff for a commit"),
        ("search", {"query": "refactor"}, "Search commit messages"),
        ("spec_impl", {}, "Get linked spec/impl pairs"),
    ],
)
class GitNode(BaseLogosNode):
    """
    AGENTESE node for Git History.

    Provides comprehensive git history access:
    - Recent commits with metadata
    - File history with blame
    - Commit diffs
    - Commit search
    - Spec/impl pair detection

    Philosophy:
        "The git history IS the implementation chronicle.
         Every commit is a witnessed decision."
    """

    def __init__(
        self,
        git_service: Any | None = None,
    ) -> None:
        self._service = git_service

    def _get_service(self) -> Any:
        if self._service is None:
            from .git_service import get_git_service

            self._service = get_git_service()
        return self._service

    @property
    def handle(self) -> str:
        return "self.git"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("history", "file_history", "blame", "diff", "search", "spec_impl")

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get recent commits",
        examples=["self.git.history", "self.git.history[limit=20]"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        commits = await self.history(observer, **kwargs)
        return CommitListRendering(commits=commits, total=len(commits))

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get recent commits from the repository",
        examples=["self.git.history", "self.git.history[limit=20]"],
    )
    async def history(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        limit: int = 50,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        service = self._get_service()
        commits = await service.get_recent_commits(limit=limit)
        return [c.to_dict() for c in commits]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get commit history for a specific file",
        examples=["self.git.file_history[path=services/self/node.py]"],
    )
    async def file_history(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        path: str = "",
        limit: int = 50,
        include_blame: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not path:
            return {"error": "path required"}
        service = self._get_service()
        history = await service.get_file_history(path, limit=limit, include_blame=include_blame)
        return history.to_dict()  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get blame information for a file",
        examples=["self.git.blame[path=services/self/node.py]"],
    )
    async def blame(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        path: str = "",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not path:
            return []
        service = self._get_service()
        blame_lines = await service.get_file_blame(path)
        return [b.to_dict() for b in blame_lines]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get diff for a commit",
        examples=["self.git.diff[sha=abc123]"],
    )
    async def diff(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        sha: str = "",
        **kwargs: Any,
    ) -> str:
        if not sha:
            return ""
        service = self._get_service()
        return await service.get_diff(sha)  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Search commit messages",
        examples=["self.git.search[query=refactor]"],
    )
    async def search(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        query: str = "",
        limit: int = 50,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        if not query:
            return []
        service = self._get_service()
        commits = await service.search_commits(query, limit=limit)
        return [c.to_dict() for c in commits]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get linked spec/impl file pairs",
        examples=["self.git.spec_impl"],
    )
    async def spec_impl(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        service = self._get_service()
        pairs = await service.get_spec_impl_pairs()
        return [p.to_dict() for p in pairs]

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        if aspect == "history":
            commits = await self.history(observer, **kwargs)
            return CommitListRendering(commits=commits, total=len(commits)).to_dict()
        elif aspect == "file_history":
            history = await self.file_history(observer, **kwargs)
            return FileHistoryRendering(history=history).to_dict()
        elif aspect == "blame":
            blame_lines = await self.blame(observer, **kwargs)
            path = kwargs.get("path", "")
            return BlameRendering(blame=blame_lines, path=path).to_dict()
        elif aspect == "diff":
            diff_text = await self.diff(observer, **kwargs)
            return {"type": "diff", "sha": kwargs.get("sha", ""), "diff": diff_text}
        elif aspect == "search":
            commits = await self.search(observer, **kwargs)
            return CommitListRendering(commits=commits, total=len(commits)).to_dict()
        elif aspect == "spec_impl":
            pairs = await self.spec_impl(observer, **kwargs)
            return {"type": "spec_impl_pairs", "pairs": pairs, "total": len(pairs)}
        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# DecisionsNode - Decision History
# =============================================================================


@dataclass(frozen=True)
class DecisionListRendering:
    """Rendering for list of decisions."""

    decisions: list[dict[str, Any]]
    total: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "decision_list",
            "decisions": self.decisions,
            "total": self.total,
        }

    def to_text(self) -> str:
        lines = [
            f"Decision History ({self.total} decisions)",
            "=" * 60,
            "",
        ]
        for dec in self.decisions[:10]:
            topic = dec.get("topic", "?")[:40]
            synthesis = dec.get("synthesis", dec.get("reasoning", ""))[:30]
            date = dec.get("timestamp", "?")[:10]
            lines.append(f"[{date}] {topic}")
            lines.append(f"         -> {synthesis}")
            lines.append("")
        if len(self.decisions) > 10:
            lines.append(f"... and {len(self.decisions) - 10} more")
        return "\n".join(lines)


@dataclass(frozen=True)
class DecisionDetailRendering:
    """Rendering for a single decision."""

    decision: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "decision_detail",
            **self.decision,
        }

    def to_text(self) -> str:
        lines = [
            f"Decision: {self.decision.get('topic', '?')}",
            "=" * 60,
            "",
            "Kent's View:",
            f"  {self.decision.get('kent_view', 'N/A')}",
            f"  Reasoning: {self.decision.get('kent_reasoning', 'N/A')}",
            "",
            "Claude's View:",
            f"  {self.decision.get('claude_view', 'N/A')}",
            f"  Reasoning: {self.decision.get('claude_reasoning', 'N/A')}",
            "",
            "Synthesis:",
            f"  {self.decision.get('synthesis', 'N/A')}",
            f"  Why: {self.decision.get('why', 'N/A')}",
        ]
        return "\n".join(lines)


@node(
    "self.decisions",
    description="Decision History - Access kg decide history",
    dependencies=("decisions_service",),
    contracts={
        "list": Response(list),
        "search": Response(dict),
        "get": Response(dict),
        "for_file": Response(list),
    },
    examples=[
        ("list", {}, "List all decisions"),
        ("list", {"limit": 20}, "List last 20 decisions"),
        ("search", {"query": "LangChain"}, "Search decisions"),
        ("get", {"decision_id": "dec-abc123"}, "Get specific decision"),
        ("for_file", {"path": "services/self/node.py"}, "Decisions about a file"),
    ],
)
class DecisionsNode(BaseLogosNode):
    """
    AGENTESE node for Decision History.

    Provides access to kg decide history:
    - List all decisions
    - Search decisions
    - Get specific decision
    - Decisions by file

    Philosophy:
        "Decisions without traces are reflexes.
         Decisions with traces are agency."
    """

    def __init__(
        self,
        decisions_service: Any | None = None,
    ) -> None:
        self._service = decisions_service

    def _get_service(self) -> Any:
        if self._service is None:
            from .decisions_service import get_decisions_service

            self._service = get_decisions_service()
        return self._service

    @property
    def handle(self) -> str:
        return "self.decisions"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("list", "search", "get", "for_file")

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="List recent decisions",
        examples=["self.decisions.list", "self.decisions.list[limit=20]"],
    )
    async def manifest(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        decisions = await self.list(observer, **kwargs)
        return DecisionListRendering(decisions=decisions, total=len(decisions))

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="List all decisions",
        examples=["self.decisions.list", "self.decisions.list[limit=20]"],
    )
    async def list(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[dict[str, Any]]:
        service = self._get_service()
        decisions = await service.list_decisions(limit=limit, offset=offset)
        return [d.to_dict() for d in decisions]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Search decisions by query",
        examples=["self.decisions.search[query=LangChain]"],
    )
    async def search(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        query: str = "",
        limit: int = 50,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not query:
            return {"decisions": [], "total_count": 0, "query": ""}
        service = self._get_service()
        result = await service.search_decisions(query, limit=limit)
        return result.to_dict()  # type: ignore[no-any-return]

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get a specific decision by ID",
        examples=["self.decisions.get[decision_id=dec-abc123]"],
    )
    async def get(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        decision_id: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not decision_id:
            return {"error": "decision_id required"}
        service = self._get_service()
        decision = await service.get_decision(decision_id)
        if decision:
            return decision.to_dict()  # type: ignore[no-any-return]
        return {"error": f"Decision not found: {decision_id}"}

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Get decisions about a specific file",
        examples=["self.decisions.for_file[path=services/self/node.py]"],
    )
    async def for_file(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        path: str = "",
        limit: int = 50,
        **kwargs: Any,
    ) -> List[dict[str, Any]]:
        if not path:
            return []
        service = self._get_service()
        decisions = await service.get_decisions_for_file(path, limit=limit)
        return [d.to_dict() for d in decisions]

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        if aspect == "list":
            decisions = await self.list(observer, **kwargs)
            return DecisionListRendering(decisions=decisions, total=len(decisions)).to_dict()
        elif aspect == "search":
            result = await self.search(observer, **kwargs)
            return result
        elif aspect == "get":
            decision = await self.get(observer, **kwargs)
            if "error" not in decision:
                return DecisionDetailRendering(decision=decision).to_dict()
            return decision
        elif aspect == "for_file":
            decisions = await self.for_file(observer, **kwargs)
            return {
                "type": "file_decisions",
                "path": kwargs.get("path", ""),
                "decisions": decisions,
            }
        else:
            return {"error": f"Unknown aspect: {aspect}"}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constitution Node
    "ConstitutionNode",
    "ConstitutionalGraphRendering",
    "DerivationChainRendering",
    "KBlockListRendering",
    "KBlockInspectionRendering",
    # Drift Node
    "DriftNode",
    "DriftReportRendering",
    "OrphanListRendering",
    "CoverageRendering",
    # Codebase Node
    "CodebaseNode",
    "CodebaseManifestRendering",
    "GraphRendering",
    "CodebaseInspectionRendering",
    "CodebaseDerivationRendering",
    # Witness Timeline Node
    "WitnessTimelineNode",
    "TimelineRendering",
    "ActivityRendering",
    "MarkSearchRendering",
    # Inspection Node
    "InspectionNode",
    "InspectionRendering",
    "QuickInspectionRendering",
    # Git Node
    "GitNode",
    "CommitListRendering",
    "FileHistoryRendering",
    "BlameRendering",
    # Decisions Node
    "DecisionsNode",
    "DecisionListRendering",
    "DecisionDetailRendering",
]
