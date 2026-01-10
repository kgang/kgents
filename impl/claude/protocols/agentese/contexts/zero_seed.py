"""
Zero Seed AGENTESE Nodes.

Exposes Zero Seed protocol operations through AGENTESE paths.

The Zero Seed Protocol (Galois Integration):
- L1 (void.axiom.*) - Fixed-point axioms (zero Galois loss)
- L2 (void.value.*) - Value derivations from axioms
- L3 (concept.goal.*) - Goal grounding in values
- L4 (concept.spec.*) - Specification of goals
- L5 (world.execution.*) - Execution of specs
- L6 (self.synthesis.*) - Reflective synthesis

Key Operations:
- contradict: Check super-additive loss between nodes
- proof-quality: Compute proof coherence via inverse Galois loss
- assign-layer: Assign layer via loss minimization
- discover-axioms: Find fixed-point axioms
- health: Check graph health via loss topography

See: spec/protocols/zero-seed1/integration.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.node import AgentMeta, BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer

logger = logging.getLogger(__name__)


# === Zero Seed Types ===


@dataclass(frozen=True)
class ContradictionResult:
    """Result of contradiction analysis via Galois loss."""

    node_a_id: str
    node_b_id: str
    strength: float  # Super-additive excess (> 0 = contradiction)
    loss_a: float
    loss_b: float
    loss_combined: float
    is_contradiction: bool
    synthesis_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_a_id": self.node_a_id,
            "node_b_id": self.node_b_id,
            "strength": self.strength,
            "loss_a": self.loss_a,
            "loss_b": self.loss_b,
            "loss_combined": self.loss_combined,
            "is_contradiction": self.is_contradiction,
            "synthesis_hint": self.synthesis_hint,
        }

    def to_text(self) -> str:
        """Human-readable representation."""
        status = "CONTRADICTION" if self.is_contradiction else "Compatible"
        lines = [
            f"Contradiction Analysis: {status}",
            f"  Strength: {self.strength:.3f}",
            f"  Loss A: {self.loss_a:.3f}",
            f"  Loss B: {self.loss_b:.3f}",
            f"  Loss Combined: {self.loss_combined:.3f}",
        ]
        if self.synthesis_hint:
            lines.append(f"  Synthesis Hint: {self.synthesis_hint}")
        return "\n".join(lines)


@dataclass(frozen=True)
class ProofQualityResult:
    """Result of proof quality assessment via Galois loss."""

    node_id: str
    coherence: float  # 1 - galois_loss
    galois_loss: float
    tier: str  # CATEGORICAL, EMPIRICAL, SOMATIC
    issues: tuple[str, ...]
    suggestions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "node_id": self.node_id,
            "coherence": self.coherence,
            "galois_loss": self.galois_loss,
            "tier": self.tier,
            "issues": list(self.issues),
            "suggestions": list(self.suggestions),
        }

    def to_text(self) -> str:
        """Human-readable representation."""
        lines = [
            f"Proof Quality ({self.tier})",
            f"  Coherence: {self.coherence:.2f}",
            f"  Galois Loss: {self.galois_loss:.3f}",
        ]
        if self.issues:
            lines.append("  Issues:")
            for issue in self.issues:
                lines.append(f"    - {issue}")
        if self.suggestions:
            lines.append("  Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"    - {suggestion}")
        return "\n".join(lines)


@dataclass(frozen=True)
class LayerAssignment:
    """Result of layer assignment via Galois loss minimization."""

    layer: int
    layer_name: str
    loss: float
    confidence: float
    loss_by_layer: dict[int, float]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "layer": self.layer,
            "layer_name": self.layer_name,
            "loss": self.loss,
            "confidence": self.confidence,
            "loss_by_layer": self.loss_by_layer,
            "rationale": self.rationale,
        }

    def to_text(self) -> str:
        """Human-readable representation."""
        lines = [
            f"Layer Assignment: L{self.layer} ({self.layer_name})",
            f"  Galois Loss: {self.loss:.3f}",
            f"  Confidence: {self.confidence:.2f}",
            f"  Rationale: {self.rationale}",
            "  Loss by Layer:",
        ]
        for layer, layer_loss in sorted(self.loss_by_layer.items()):
            marker = " <--" if layer == self.layer else ""
            lines.append(f"    L{layer}: {layer_loss:.3f}{marker}")
        return "\n".join(lines)


@dataclass(frozen=True)
class AxiomCandidate:
    """A candidate axiom discovered via fixed-point finding."""

    text: str
    source_path: str
    galois_loss: float
    is_fixed_point: bool
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "text": self.text,
            "source_path": self.source_path,
            "galois_loss": self.galois_loss,
            "is_fixed_point": self.is_fixed_point,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class AxiomDiscoveryResult:
    """Result of axiom discovery via fixed-point computation."""

    candidates: tuple[AxiomCandidate, ...]
    total_scanned: int
    fixed_points_found: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "total_scanned": self.total_scanned,
            "fixed_points_found": self.fixed_points_found,
        }

    def to_text(self) -> str:
        """Human-readable representation."""
        lines = [
            f"Axiom Discovery: {self.fixed_points_found} fixed points found",
            f"  Total scanned: {self.total_scanned}",
            "",
        ]
        for i, candidate in enumerate(self.candidates, 1):
            fp_marker = "[FP]" if candidate.is_fixed_point else "[NF]"
            lines.append(f"{i}. {fp_marker} {candidate.text[:60]}...")
            lines.append(
                f"   Loss: {candidate.galois_loss:.4f}, Confidence: {candidate.confidence:.2f}"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class GraphHealthReport:
    """Health assessment of Zero Seed graph via Galois loss topography."""

    overall_loss: float
    is_healthy: bool
    weak_edge_count: int
    high_loss_node_count: int
    unstable_region_count: int
    critical_issues: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_loss": self.overall_loss,
            "is_healthy": self.is_healthy,
            "weak_edge_count": self.weak_edge_count,
            "high_loss_node_count": self.high_loss_node_count,
            "unstable_region_count": self.unstable_region_count,
            "critical_issues": list(self.critical_issues),
        }

    def to_text(self) -> str:
        """Human-readable representation."""
        status = "HEALTHY" if self.is_healthy else "UNHEALTHY"
        lines = [
            f"Graph Health: {status}",
            f"  Overall Loss: {self.overall_loss:.3f}",
            f"  Weak Edges: {self.weak_edge_count}",
            f"  High-Loss Nodes: {self.high_loss_node_count}",
            f"  Unstable Regions: {self.unstable_region_count}",
        ]
        if self.critical_issues:
            lines.append("  Critical Issues:")
            for issue in self.critical_issues:
                lines.append(f"    - {issue}")
        return "\n".join(lines)


# === Layer Names ===

LAYER_NAMES: dict[int, str] = {
    1: "Axiom",
    2: "Value",
    3: "Goal",
    4: "Spec",
    5: "Execution",
    6: "Synthesis",
    7: "Meta",
}


# === L1: void.axiom.* - Axiom Layer ===


@node(
    "void.axiom",
    description="L1 Axiom operations - fixed-point discovery and management",
    examples=[
        ("discover", {"constitution_path": "spec/principles/CONSTITUTION.md"}, "Discover axioms"),
        ("manifest", {}, "View current axioms"),
    ],
)
@dataclass
class AxiomNode(BaseLogosNode):
    """
    L1 Axiom Layer Node.

    Axioms are zero-loss fixed points under Galois restructuring.
    They form the bedrock of the Zero Seed graph.
    """

    _handle: str = "void.axiom"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View discovered axioms - the fixed points of your system",
        "discover": "Find axioms via Galois fixed-point computation",
        "validate": "Check if a statement qualifies as an axiom",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("discover", "validate")
        return ()

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View discovered axioms",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the axiom layer state."""
        # Placeholder implementation - would query actual axiom store
        return BasicRendering(
            summary="L1 Axioms (void.axiom)",
            content="Zero-loss fixed points discovered from constitution.\n\nNo axioms loaded yet. Use 'discover' to find axioms.",
            metadata={
                "layer": 1,
                "layer_name": "Axiom",
                "axiom_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.GENERATION,
        description="Discover axioms via Galois fixed-point computation",
        effects=[Effect.READS("constitution")],
    )
    async def discover(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        constitution_path: str | None = None,
        threshold: float = 0.05,
        **kwargs: Any,
    ) -> Renderable:
        """
        Discover axioms from constitution files.

        Args:
            observer: Observer context
            constitution_path: Path to constitution file (optional)
            threshold: Galois loss threshold for fixed-point detection (default: 0.05)

        Returns:
            AxiomDiscoveryResult
        """
        # Placeholder - would implement actual Galois loss computation
        result = AxiomDiscoveryResult(
            candidates=(
                AxiomCandidate(
                    text="Tasteful > feature-complete",
                    source_path=constitution_path or "spec/principles/CONSTITUTION.md",
                    galois_loss=0.01,
                    is_fixed_point=True,
                    confidence=0.99,
                ),
                AxiomCandidate(
                    text="The Mirror Test: Does K-gent feel like me on my best day?",
                    source_path=constitution_path or "spec/principles/CONSTITUTION.md",
                    galois_loss=0.02,
                    is_fixed_point=True,
                    confidence=0.98,
                ),
            ),
            total_scanned=10,
            fixed_points_found=2,
        )

        return BasicRendering(
            summary=f"Axiom Discovery: {result.fixed_points_found} fixed points",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "discover":
            return await self.discover(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === L2: void.value.* - Value Layer ===


@node(
    "void.value",
    description="L2 Value operations - value derivation from axioms",
    examples=[
        ("manifest", {}, "View derived values"),
        ("contradict", {"node_a": "value1", "node_b": "value2"}, "Check contradiction"),
    ],
)
@dataclass
class ValueNode(BaseLogosNode):
    """
    L2 Value Layer Node.

    Values are derived from axioms with minimal Galois loss.
    """

    _handle: str = "void.value"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View value derivations from axioms",
        "contradict": "Check super-additive loss between values",
        "derive": "Derive a new value from axioms",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("contradict", "derive")
        return ("contradict",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View derived values",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the value layer state."""
        return BasicRendering(
            summary="L2 Values (void.value)",
            content="Values derived from axioms with minimal Galois loss.\n\nUse 'contradict' to check value compatibility.",
            metadata={
                "layer": 2,
                "layer_name": "Value",
                "value_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.INTROSPECTION,
        description="Check super-additive loss between two nodes",
        effects=[Effect.READS("graph")],
    )
    async def contradict(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        node_a: str,
        node_b: str,
        tolerance: float = 0.05,
        **kwargs: Any,
    ) -> Renderable:
        """
        Check if two nodes contradict via super-additive Galois loss.

        Args:
            observer: Observer context
            node_a: First node ID
            node_b: Second node ID
            tolerance: Tolerance for super-additivity (default: 0.05)

        Returns:
            ContradictionResult
        """
        # Placeholder - would compute actual Galois losses
        loss_a = 0.15
        loss_b = 0.18
        loss_combined = 0.45
        strength = loss_combined - (loss_a + loss_b)
        is_contradiction = strength > tolerance

        result = ContradictionResult(
            node_a_id=node_a,
            node_b_id=node_b,
            strength=strength,
            loss_a=loss_a,
            loss_b=loss_b,
            loss_combined=loss_combined,
            is_contradiction=is_contradiction,
            synthesis_hint="Consider focusing on shared grounding" if is_contradiction else None,
        )

        return BasicRendering(
            summary=f"Contradiction: {'YES' if is_contradiction else 'NO'} ({strength:.3f})",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "contradict":
            return await self.contradict(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === L3: concept.goal.* - Goal Layer ===


@node(
    "concept.goal",
    description="L3 Goal operations - goal grounding in values",
    examples=[
        ("manifest", {}, "View current goals"),
        ("assign-layer", {"content": "Build a tasteful agent"}, "Assign layer to content"),
    ],
)
@dataclass
class GoalNode(BaseLogosNode):
    """
    L3 Goal Layer Node.

    Goals are grounded in values and assessed for justification loss.
    """

    _handle: str = "concept.goal"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View goals and their value justifications",
        "assign-layer": "Determine the natural layer for content via Galois loss",
        "ground": "Ground a goal in specific values",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("assign-layer", "ground")
        return ("assign-layer",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View goals and justifications",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the goal layer state."""
        return BasicRendering(
            summary="L3 Goals (concept.goal)",
            content="Goals grounded in values with justification chains.\n\nUse 'assign-layer' to determine content layer.",
            metadata={
                "layer": 3,
                "layer_name": "Goal",
                "goal_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.INTROSPECTION,
        description="Assign content to natural layer via Galois loss minimization",
    )
    async def assign_layer(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        content: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Assign content to the layer where it has minimal Galois loss.

        Args:
            observer: Observer context
            content: Content to assign

        Returns:
            LayerAssignment
        """
        # Placeholder - would compute losses across all layers
        loss_by_layer = {
            1: 0.85,
            2: 0.62,
            3: 0.18,
            4: 0.34,
            5: 0.45,
            6: 0.52,
            7: 0.71,
        }
        best_layer = min(loss_by_layer, key=loss_by_layer.get)  # type: ignore[arg-type]
        best_loss = loss_by_layer[best_layer]

        result = LayerAssignment(
            layer=best_layer,
            layer_name=LAYER_NAMES[best_layer],
            loss=best_loss,
            confidence=1.0 - best_loss,
            loss_by_layer=loss_by_layer,
            rationale=f"Content naturally lives at L{best_layer} due to minimal Galois loss",
        )

        return BasicRendering(
            summary=f"Layer Assignment: L{best_layer} ({LAYER_NAMES[best_layer]})",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        # Handle hyphenated aspect name
        if aspect == "assign-layer":
            return await self.assign_layer(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === L4: concept.spec.* - Spec Layer ===


@node(
    "concept.spec",
    description="L4 Spec operations - specification of goals",
    examples=[
        ("manifest", {}, "View specifications"),
        ("proof-quality", {"node_id": "spec-123"}, "Check proof coherence"),
    ],
)
@dataclass
class SpecNode(BaseLogosNode):
    """
    L4 Spec Layer Node.

    Specs are goal realizations with Toulmin proofs.
    """

    _handle: str = "concept.spec"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View specifications and their goal groundings",
        "proof-quality": "Compute proof coherence via inverse Galois loss",
        "validate": "Validate a spec against its goal",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("proof-quality", "validate")
        return ("proof-quality",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View specifications",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the spec layer state."""
        return BasicRendering(
            summary="L4 Specs (concept.spec)",
            content="Specifications with Toulmin proofs.\n\nUse 'proof-quality' to assess coherence.",
            metadata={
                "layer": 4,
                "layer_name": "Spec",
                "spec_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.INTROSPECTION,
        description="Compute proof coherence via inverse Galois loss",
        effects=[Effect.READS("proofs")],
    )
    async def proof_quality(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        node_id: str,
        **kwargs: Any,
    ) -> Renderable:
        """
        Assess proof quality via Galois loss.

        coherence = 1 - galois_loss

        Args:
            observer: Observer context
            node_id: Node to assess

        Returns:
            ProofQualityResult
        """
        # Placeholder - would compute actual Galois loss on proof
        galois_loss = 0.22
        coherence = 1.0 - galois_loss

        # Classify tier by loss
        if galois_loss < 0.1:
            tier = "CATEGORICAL"
        elif galois_loss < 0.3:
            tier = "EMPIRICAL"
        else:
            tier = "SOMATIC"

        issues = []
        suggestions = []
        if galois_loss > 0.2:
            issues.append("Proof structure doesn't survive modularization")
        if galois_loss > 0.4:
            issues.append("Warrant-claim linkage is weak")
            suggestions.append("Strengthen the warrant with more evidence")

        result = ProofQualityResult(
            node_id=node_id,
            coherence=coherence,
            galois_loss=galois_loss,
            tier=tier,
            issues=tuple(issues),
            suggestions=tuple(suggestions),
        )

        return BasicRendering(
            summary=f"Proof Quality: {coherence:.2f} ({tier})",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        # Handle hyphenated aspect name
        if aspect == "proof-quality":
            return await self.proof_quality(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === L5: world.execution.* - Execution Layer ===


@node(
    "world.execution",
    description="L5 Execution operations - execution of specs in the world",
    examples=[
        ("manifest", {}, "View execution state"),
        ("health", {}, "Check graph health"),
    ],
)
@dataclass
class ExecutionNode(BaseLogosNode):
    """
    L5 Execution Layer Node.

    Execution is where specs meet the world.
    """

    _handle: str = "world.execution"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View execution state and deviations",
        "health": "Check graph health via loss topography",
        "trace": "Trace execution path for a node",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("health", "trace")
        return ("health",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View execution state",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the execution layer state."""
        return BasicRendering(
            summary="L5 Execution (world.execution)",
            content="Execution layer - where specs meet the world.\n\nUse 'health' to check graph integrity.",
            metadata={
                "layer": 5,
                "layer_name": "Execution",
                "execution_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.INTROSPECTION,
        description="Check graph health via Galois loss topography",
        effects=[Effect.READS("graph")],
    )
    async def health(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """
        Assess graph health via Galois loss topography.

        Args:
            observer: Observer context

        Returns:
            GraphHealthReport
        """
        # Placeholder - would compute actual graph health
        overall_loss = 0.28
        is_healthy = overall_loss < 0.3

        result = GraphHealthReport(
            overall_loss=overall_loss,
            is_healthy=is_healthy,
            weak_edge_count=3,
            high_loss_node_count=1,
            unstable_region_count=0,
            critical_issues=() if is_healthy else ("Overall loss exceeds healthy threshold",),
        )

        return BasicRendering(
            summary=f"Graph Health: {'HEALTHY' if is_healthy else 'UNHEALTHY'} ({overall_loss:.2f})",
            content=result.to_text(),
            metadata=result.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "health":
            return await self.health(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === L6: self.synthesis.* - Synthesis Layer ===


@node(
    "self.synthesis",
    description="L6 Synthesis operations - reflective synthesis and integration",
    examples=[
        ("manifest", {}, "View synthesis state"),
        ("reflect", {"node_id": "synth-123"}, "Reflect on synthesis"),
    ],
)
@dataclass
class SynthesisNode(BaseLogosNode):
    """
    L6 Synthesis Layer Node.

    Synthesis reflects on execution and updates the graph.
    """

    _handle: str = "self.synthesis"

    @property
    def handle(self) -> str:
        return self._handle

    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "View synthesis state and pending integrations",
        "reflect": "Trigger reflective synthesis on a node",
        "integrate": "Integrate synthesis results into the graph",
    }

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        if archetype in ("developer", "architect"):
            return ("reflect", "integrate")
        return ("reflect",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        description="View synthesis state",
    )
    async def manifest(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        **kwargs: Any,
    ) -> Renderable:
        """Manifest the synthesis layer state."""
        return BasicRendering(
            summary="L6 Synthesis (self.synthesis)",
            content="Synthesis layer - reflective integration.\n\nUse 'reflect' to synthesize insights.",
            metadata={
                "layer": 6,
                "layer_name": "Synthesis",
                "synthesis_count": 0,
            },
        )

    @aspect(
        category=AspectCategory.MUTATION,
        description="Trigger reflective synthesis",
        effects=[Effect.READS("graph"), Effect.WRITES("synthesis")],
    )
    async def reflect(
        self,
        observer: "Umwelt[Any, Any] | Observer",
        node_id: str | None = None,
        **kwargs: Any,
    ) -> Renderable:
        """
        Trigger reflective synthesis.

        Args:
            observer: Observer context
            node_id: Optional specific node to reflect on

        Returns:
            Synthesis result
        """
        return BasicRendering(
            summary="Synthesis Reflection",
            content=f"Reflecting on {'node ' + node_id if node_id else 'entire graph'}...\n\nSynthesis integration pending.",
            metadata={
                "node_id": node_id,
                "status": "pending",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations."""
        if aspect == "reflect":
            return await self.reflect(observer, **kwargs)
        raise ValueError(f"Unknown aspect: {aspect}")


# === Factory Functions ===


def get_axiom_node() -> AxiomNode:
    """Get an AxiomNode instance."""
    return AxiomNode()


def get_value_node() -> ValueNode:
    """Get a ValueNode instance."""
    return ValueNode()


def get_goal_node() -> GoalNode:
    """Get a GoalNode instance."""
    return GoalNode()


def get_spec_node() -> SpecNode:
    """Get a SpecNode instance."""
    return SpecNode()


def get_execution_node() -> ExecutionNode:
    """Get an ExecutionNode instance."""
    return ExecutionNode()


def get_synthesis_node() -> SynthesisNode:
    """Get a SynthesisNode instance."""
    return SynthesisNode()


# === Exports ===

__all__ = [
    # Nodes
    "AxiomNode",
    "ValueNode",
    "GoalNode",
    "SpecNode",
    "ExecutionNode",
    "SynthesisNode",
    # Result types
    "ContradictionResult",
    "ProofQualityResult",
    "LayerAssignment",
    "AxiomCandidate",
    "AxiomDiscoveryResult",
    "GraphHealthReport",
    # Factory functions
    "get_axiom_node",
    "get_value_node",
    "get_goal_node",
    "get_spec_node",
    "get_execution_node",
    "get_synthesis_node",
    # Constants
    "LAYER_NAMES",
]
