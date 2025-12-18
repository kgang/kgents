"""
AGENTESE Self.System Context - Autopoietic Kernel Interface.

self.system.* handles for introspection and self-modification:
- self.system.manifest    - Project to observer's view
- self.system.audit       - Drift detection (spec vs impl)
- self.system.compile     - Spec → Impl generation
- self.system.reflect     - Impl → Spec extraction
- self.system.evolve      - Apply mutations
- self.system.witness     - History of changes (N-gent trace)

This is the autopoietic interface - the system's ability to describe,
modify, and regenerate itself.

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, Effect, aspect
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Types ===


class DriftStatus(str, Enum):
    """Status of spec-impl alignment."""

    ALIGNED = "aligned"  # Spec and impl match
    DIVERGED = "diverged"  # Spec and impl differ
    MISSING_SPEC = "missing_spec"  # Impl exists without spec
    MISSING_IMPL = "missing_impl"  # Spec exists without impl
    UNKNOWN = "unknown"  # Cannot determine


@dataclass(frozen=True)
class DriftReport:
    """Report of spec-impl drift for a single module."""

    module: str
    status: DriftStatus
    spec_path: str | None = None
    impl_path: str | None = None
    spec_hash: str | None = None
    impl_hash: str | None = None
    details: str = ""


@dataclass
class AuditResult:
    """Result of a full system audit."""

    timestamp: datetime
    total_modules: int
    aligned: int
    diverged: int
    missing_spec: int
    missing_impl: int
    reports: list[DriftReport] = field(default_factory=list)
    autopoiesis_score: float = 0.0

    @property
    def healthy(self) -> bool:
        """Is the system healthy (all aligned)?"""
        return self.diverged == 0 and self.missing_impl == 0


@dataclass
class CompileResult:
    """Result of compiling a spec to impl."""

    spec_path: str
    impl_path: str
    success: bool
    generated_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class ReflectResult:
    """Result of reflecting impl to spec."""

    impl_path: str
    spec_content: str
    confidence: float = 0.0  # How confident in extraction


# === Affordances ===


SYSTEM_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "audit",
    "compile",
    "reflect",
    "evolve",
    "witness",
)


# === Node Implementation ===


@node("self.system", description="Autopoietic kernel interface")
@dataclass
class SystemNode(BaseLogosNode):
    """
    self.system - The autopoietic kernel interface.

    Provides introspection and self-modification capabilities for kgents.
    This is the system's ability to describe, modify, and regenerate itself.

    The Three Functors:
    - Compile: SpecCat → ImplCat (generate implementation from spec)
    - Project: ImplCat → PathCat (make service discoverable)
    - Reflect: ImplCat → SpecCat (extract spec from implementation)

    Autopoiesis Fixed Point: Reflect(Compile(S)) ≅ S
    """

    _handle: str = "self.system"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes get same affordances for system introspection."""
        return SYSTEM_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View system architecture and health",
    )
    async def manifest(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        What is kgents? Project to observer's view.

        Returns the metaphysical agent stack (AD-009) with current health metrics.
        """
        # Get observer archetype
        archetype = "guest"
        if hasattr(observer, "archetype"):
            archetype = observer.archetype
        elif hasattr(observer, "dna"):
            archetype = getattr(observer.dna, "archetype", "guest")

        # Build stack visualization
        stack = """
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
"""
        return BasicRendering(
            summary="kgents Metaphysical Agent Stack (AD-009)",
            content=stack,
            metadata={
                "observer": archetype,
                "route": "/system",
                "stack_layers": 7,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="Detect spec-impl drift across the system",
    )
    async def audit(self, observer: Observer | "Umwelt[Any, Any]") -> Renderable:
        """
        What needs fixing? Run drift detection.

        Compares specs against implementations and calculates autopoiesis score.
        """
        # Collect audit data
        # TODO: Implement actual drift detection
        audit = AuditResult(
            timestamp=datetime.now(),
            total_modules=0,
            aligned=0,
            diverged=0,
            missing_spec=0,
            missing_impl=0,
            reports=[],
            autopoiesis_score=0.0,
        )

        # For now, return placeholder
        content = f"""
## System Audit

**Timestamp:** {audit.timestamp.isoformat()}
**Autopoiesis Score:** {audit.autopoiesis_score:.1%}

### Module Status
- Total: {audit.total_modules}
- Aligned: {audit.aligned}
- Diverged: {audit.diverged}
- Missing Spec: {audit.missing_spec}
- Missing Impl: {audit.missing_impl}

### Phoenix Metric
Autopoiesis Score = (Systems using categorical foundation) / (Total systems)

Current: ~0.3 (estimated)
Target:  ≥0.9

### Known Issues
- 3 rogue operads need unification (F-gent, Atelier, SelfGrow)
- 2 Crown Jewels not implemented (Coalition, Domain Simulation)
- AGENTESE discovery incomplete in gateway

Run `kg self.system.evolve` to apply fixes.
"""
        return BasicRendering(
            summary=f"System Audit: {audit.autopoiesis_score:.1%} autopoiesis",
            content=content,
            metadata={
                "total_modules": audit.total_modules,
                "autopoiesis_score": audit.autopoiesis_score,
                "healthy": audit.healthy,
            },
        )

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.WRITES("impl/")],
        help="Generate implementation from spec",
    )
    async def compile(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        spec_path: str | None = None,
    ) -> Renderable:
        """
        Spec → Impl: Generate implementation from specification.

        The Compile functor transforms SpecCat → ImplCat.
        """
        if not spec_path:
            return BasicRendering(
                summary="Compile requires spec_path",
                content="Usage: `kg self.system.compile spec_path=spec/path/to/spec.md`",
                metadata={"error": "missing_spec_path"},
            )

        # TODO: Implement actual compilation
        result = CompileResult(
            spec_path=spec_path,
            impl_path="",
            success=False,
            errors=["Compilation not yet implemented"],
        )

        return BasicRendering(
            summary=f"Compile: {spec_path}",
            content=f"Would compile {spec_path} → impl/",
            metadata={
                "spec_path": result.spec_path,
                "success": result.success,
            },
        )

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.READS("impl/")],
        help="Extract spec from implementation",
    )
    async def reflect(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        impl_path: str | None = None,
    ) -> Renderable:
        """
        Impl → Spec: Extract specification from implementation.

        The Reflect functor transforms ImplCat → SpecCat.
        Used to verify autopoiesis: Reflect(Compile(S)) ≅ S
        """
        if not impl_path:
            return BasicRendering(
                summary="Reflect requires impl_path",
                content="Usage: `kg self.system.reflect impl_path=impl/claude/path`",
                metadata={"error": "missing_impl_path"},
            )

        # TODO: Implement actual reflection
        result = ReflectResult(
            impl_path=impl_path,
            spec_content="",
            confidence=0.0,
        )

        return BasicRendering(
            summary=f"Reflect: {impl_path}",
            content=f"Would extract spec from {impl_path}",
            metadata={
                "impl_path": result.impl_path,
                "confidence": result.confidence,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("impl/"), Effect.WRITES("spec/")],
        help="Apply evolution/mutation to system",
    )
    async def evolve(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        mutation: str | None = None,
    ) -> Renderable:
        """
        Apply consolidation/mutation to the system.

        Requires explicit confirmation from observer with appropriate capabilities.
        """
        # Check observer has evolve capability
        capabilities: frozenset[str] = frozenset()
        if hasattr(observer, "capabilities"):
            capabilities = observer.capabilities

        if "evolve" not in capabilities and "admin" not in capabilities:
            return BasicRendering(
                summary="Evolve requires elevated capabilities",
                content="Observer must have 'evolve' or 'admin' capability",
                metadata={"error": "insufficient_capabilities"},
            )

        if not mutation:
            return BasicRendering(
                summary="Evolve requires mutation specification",
                content="Usage: `kg self.system.evolve mutation=operad_unification`",
                metadata={"error": "missing_mutation"},
            )

        # TODO: Implement mutation application
        return BasicRendering(
            summary=f"Evolve: {mutation}",
            content=f"Would apply mutation: {mutation}",
            metadata={
                "mutation": mutation,
                "applied": False,
            },
        )

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View history of system changes",
    )
    async def witness(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        limit: int = 10,
    ) -> Renderable:
        """
        History of changes: N-gent trace of system evolution.

        Shows recent commits, mutations, and evolution events.
        """
        # TODO: Implement actual history
        return BasicRendering(
            summary="System History",
            content=f"Would show last {limit} system events",
            metadata={
                "limit": limit,
                "events": [],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        aspect_methods: dict[str, Any] = {
            "audit": self.audit,
            "compile": self.compile,
            "reflect": self.reflect,
            "evolve": self.evolve,
            "witness": self.witness,
        }

        if aspect in aspect_methods:
            return await aspect_methods[aspect](observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory Functions ===

_system_node: SystemNode | None = None


def get_system_node() -> SystemNode:
    """Get or create the singleton SystemNode."""
    global _system_node
    if _system_node is None:
        _system_node = SystemNode()
    return _system_node


def create_system_node() -> SystemNode:
    """Create a new SystemNode (for testing)."""
    return SystemNode()


# === Exports ===

__all__ = [
    # Types
    "DriftStatus",
    "DriftReport",
    "AuditResult",
    "CompileResult",
    "ReflectResult",
    # Constants
    "SYSTEM_AFFORDANCES",
    # Node
    "SystemNode",
    # Factory
    "get_system_node",
    "create_system_node",
]
