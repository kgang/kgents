"""
Membrane CLI - Command surface for topological perception.

Implements the Membrane Protocol from spec/protocols/membrane.md:

Perception Verbs:
- observe: Full topological observation (curvature, void, flow, dampening)
- sense: Quick shape intuition (dominant shapes only)
- trace: Follow a thread (momentum of specific topic)
- map: Render the semantic manifold

Gesture Verbs:
- touch: Acknowledge a shape (mark as seen)
- name: Give voice to a void (create principle for implicit pattern)
- hold: Preserve productive tension
- release: Allow natural resolution

The Membrane is not a boundary - it is a zone of becoming.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .cli_types import (
    BudgetLevel,
    BudgetStatus,
    CLIContext,
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
    OutputFormat,
)

# =============================================================================
# Membrane Types (from spec/protocols/membrane.md)
# =============================================================================


@dataclass(frozen=True)
class SemanticCurvature:
    """
    A region of high semantic tension.

    From membrane.md: Where meaning bends under tension.
    High curvature indicates contested concepts, load-bearing ideas,
    or points of potential transformation.
    """

    shape_id: str  # e.g., "SHAPE-47-curve"
    centroid_topic: str
    radius: float  # How far the bending extends
    intensity: float  # How sharp the curve (0.0-1.0)
    attractors: tuple[str, ...]  # Concepts pulled toward this region
    repellers: tuple[str, ...]  # Concepts pushed away
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape_id": self.shape_id,
            "type": "curvature",
            "topic": self.centroid_topic,
            "radius": self.radius,
            "intensity": self.intensity,
            "attractors": list(self.attractors),
            "repellers": list(self.repellers),
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class SemanticVoid:
    """
    A topological hole in the meaning manifold.

    From membrane.md: Ma (間) - the pregnant emptiness.
    The void is not absence; it is active negative space.
    """

    shape_id: str  # e.g., "SHAPE-12-void"
    boundary: tuple[str, ...]  # Concepts that ring the void
    depth: float  # How pronounced the absence (0.0-1.0)
    persistence: float  # How stable across time
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape_id": self.shape_id,
            "type": "void",
            "boundary": list(self.boundary),
            "depth": self.depth,
            "persistence": self.persistence,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class SemanticMomentum:
    """
    The motion of meaning through time.

    From membrane.md: p⃗ = m · v⃗
    Tracks how topics gain/lose energy and change meaning.
    """

    shape_id: str  # e.g., "SHAPE-103-flow"
    topic: str
    mass: float  # Attention/reference density
    velocity_magnitude: float  # Speed of drift
    velocity_direction: str  # Semantic direction ("toward X", "away from Y")
    is_conserved: bool  # Is momentum stable?
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape_id": self.shape_id,
            "type": "momentum",
            "topic": self.topic,
            "mass": self.mass,
            "velocity": {
                "magnitude": self.velocity_magnitude,
                "direction": self.velocity_direction,
            },
            "conserved": self.is_conserved,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class DampeningField:
    """
    A region where emotional expression is suppressed.

    From membrane.md: When variance compresses, something is being suppressed.
    """

    shape_id: str  # e.g., "SHAPE-89-damp"
    trigger: str  # What topic activates the field
    compression_ratio: float  # How much variance is lost (0.0-1.0)
    affected_count: int  # How many items are affected
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape_id": self.shape_id,
            "type": "dampening",
            "trigger": self.trigger,
            "compression_ratio": self.compression_ratio,
            "affected_count": self.affected_count,
            "interpretation": self.interpretation,
        }


# Union type for shapes
SemanticShape = SemanticCurvature | SemanticVoid | SemanticMomentum | DampeningField


@dataclass
class MembraneObserveResult:
    """Result from membrane observe command."""

    integrity_score: float
    trend: str  # "improving" (▵), "stable", "declining" (▿)
    shapes: list[SemanticShape]
    suggestion: str
    observed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "integrity_score": self.integrity_score,
            "trend": self.trend,
            "shapes": [s.to_dict() for s in self.shapes],
            "suggestion": self.suggestion,
            "observed_at": self.observed_at.isoformat(),
        }


@dataclass
class MembraneSenseResult:
    """Result from membrane sense command - quick shape intuition."""

    integrity_score: float
    dominant_shape: SemanticShape | None
    shape_count: int
    sensed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "integrity_score": self.integrity_score,
            "dominant_shape": self.dominant_shape.to_dict()
            if self.dominant_shape
            else None,
            "shape_count": self.shape_count,
            "sensed_at": self.sensed_at.isoformat(),
        }


@dataclass
class MembraneTraceResult:
    """Result from membrane trace command - follow topic momentum."""

    topic: str
    momentum: SemanticMomentum | None
    history: list[dict[str, Any]]  # Historical momentum snapshots
    traced_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "momentum": self.momentum.to_dict() if self.momentum else None,
            "history": self.history,
            "traced_at": self.traced_at.isoformat(),
        }


# =============================================================================
# Membrane CLI
# =============================================================================


class MembraneCLI:
    """
    CLI interface for Membrane Protocol.

    The Membrane perceives shape - curvature, void, flow, dampening -
    and provides gestures to acknowledge and interact with what is perceived.
    """

    def __init__(self) -> None:
        """Initialize Membrane CLI."""
        self._shape_counter = 0
        self._shapes: list[SemanticShape] = []
        self._acknowledged: set[str] = set()  # Shape IDs that have been touched

    def _next_shape_id(self, shape_type: str) -> str:
        """Generate next shape identifier."""
        self._shape_counter += 1
        abbrev = {
            "curvature": "curve",
            "void": "void",
            "momentum": "flow",
            "dampening": "damp",
        }.get(shape_type, shape_type[:4])
        return f"SHAPE-{self._shape_counter:02d}-{abbrev}"

    async def observe(
        self,
        target_path: Path | None = None,
        ctx: CLIContext | None = None,
    ) -> CommandResult[MembraneObserveResult]:
        """
        Full topological observation.

        Perceives curvature, void, flow, and dampening.
        This is the full observation - use 'sense' for quick intuition.

        Usage: kgents membrane observe
               kgents observe  (alias)
        """
        ctx = ctx or CLIContext()
        start_time = time.time()

        # For now, we detect shapes from the current directory structure
        # In full implementation, this would integrate with:
        # - L-gent semantic analysis
        # - Git history (commit patterns)
        # - Code structure (module dependencies)

        target = target_path or Path.cwd()

        if ctx.is_sanctuary(target):
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.ETHICAL,
                    severity=ErrorSeverity.FAILURE,
                    code="SANCTUARY_VIOLATION",
                    message=f"Path is in sanctuary: {target}",
                )
            )

        try:
            shapes = await self._detect_shapes(target, ctx)
            self._shapes = shapes

            # Calculate integrity from shape intensities
            if shapes:
                avg_intensity = sum(
                    getattr(s, "intensity", 0.5) or getattr(s, "depth", 0.5) or 0.5
                    for s in shapes
                ) / len(shapes)
                integrity = 1.0 - (
                    avg_intensity * 0.5
                )  # Higher intensity = lower integrity
            else:
                integrity = 1.0

            # Generate suggestion based on most significant shape
            suggestion = self._generate_suggestion(shapes)

            duration_ms = int((time.time() - start_time) * 1000)

            result = MembraneObserveResult(
                integrity_score=integrity,
                trend="stable",  # TODO: Track over time
                shapes=shapes,
                suggestion=suggestion,
            )

            return CommandResult.ok(result, duration_ms=duration_ms, budget=ctx.budget)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="OBSERVATION_ERROR",
                    message=str(e),
                ),
                duration_ms=duration_ms,
            )

    async def sense(
        self,
        ctx: CLIContext | None = None,
    ) -> CommandResult[MembraneSenseResult]:
        """
        Quick shape intuition.

        Returns only the dominant shape. Use 'observe' for full analysis.
        Target: <100ms

        Usage: kgents membrane sense
               kgents sense  (alias)
        """
        ctx = ctx or CLIContext()
        start_time = time.time()

        # Use cached shapes if recent, otherwise quick detect
        if not self._shapes:
            # Quick detection - just check for obvious patterns
            shapes = await self._quick_detect_shapes(ctx)
        else:
            shapes = self._shapes

        dominant = (
            max(
                shapes,
                key=lambda s: getattr(s, "intensity", 0)
                or getattr(s, "depth", 0)
                or 0.5,
            )
            if shapes
            else None
        )

        # Calculate quick integrity
        if dominant:
            intensity = getattr(dominant, "intensity", 0.5) or getattr(
                dominant, "depth", 0.5
            )
            integrity = 1.0 - (intensity * 0.3)
        else:
            integrity = 1.0

        duration_ms = int((time.time() - start_time) * 1000)

        result = MembraneSenseResult(
            integrity_score=integrity,
            dominant_shape=dominant,
            shape_count=len(shapes),
        )

        return CommandResult.ok(result, duration_ms=duration_ms)

    async def trace(
        self,
        topic: str,
        ctx: CLIContext | None = None,
    ) -> CommandResult[MembraneTraceResult]:
        """
        Follow a thread - track topic momentum over time.

        Usage: kgents membrane trace "authentication"
               kgents trace "authentication"  (alias)
        """
        ctx = ctx or CLIContext()
        start_time = time.time()

        # Find momentum for this topic
        momentum = None
        for shape in self._shapes:
            if (
                isinstance(shape, SemanticMomentum)
                and topic.lower() in shape.topic.lower()
            ):
                momentum = shape
                break

        # If not found in cached shapes, create placeholder
        if not momentum:
            momentum = SemanticMomentum(
                shape_id=self._next_shape_id("momentum"),
                topic=topic,
                mass=0.5,
                velocity_magnitude=0.0,
                velocity_direction="stable",
                is_conserved=True,
                interpretation=f"No significant momentum detected for '{topic}'",
            )

        duration_ms = int((time.time() - start_time) * 1000)

        result = MembraneTraceResult(
            topic=topic,
            momentum=momentum,
            history=[],  # TODO: D-gent integration for history
        )

        return CommandResult.ok(result, duration_ms=duration_ms)

    async def touch(
        self,
        shape_id: str,
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict[str, Any]]:
        """
        Acknowledge a shape - mark as seen, reduce its urgency.

        Usage: kgents membrane touch SHAPE-12-void
               kgents touch SHAPE-12  (alias)
        """
        ctx = ctx or CLIContext()

        # Find the shape
        shape = None
        for s in self._shapes:
            if s.shape_id == shape_id or s.shape_id.startswith(shape_id):
                shape = s
                break

        if not shape:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="SHAPE_NOT_FOUND",
                    message=f"Shape not found: {shape_id}",
                    suggestions=(
                        "Run 'membrane observe' first to detect shapes",
                        "Check shape ID with 'membrane sense'",
                    ),
                )
            )

        self._acknowledged.add(shape.shape_id)

        return CommandResult.ok(
            {
                "acknowledged": True,
                "shape_id": shape.shape_id,
                "interpretation": shape.interpretation,
            }
        )

    async def name(
        self,
        description: str,
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict[str, Any]]:
        """
        Give voice to a void - create explicit principle for implicit pattern.

        This is the most powerful gesture: naming the unsaid.

        Usage: kgents membrane name "We avoid discussing error handling"
               kgents name "We avoid discussing deadlines"  (alias)
        """
        ctx = ctx or CLIContext()

        # Find the deepest void to associate this naming with
        voids = [s for s in self._shapes if isinstance(s, SemanticVoid)]
        associated_void = max(voids, key=lambda v: v.depth) if voids else None

        # Create a new principle from the naming
        # In full implementation, this would:
        # 1. Create a new Thesis in the Deontic lattice
        # 2. Persist via D-gent
        # 3. Update the void's interpretation

        result = {
            "named": True,
            "statement": description,
            "associated_void": associated_void.shape_id if associated_void else None,
            "suggestion": "The void persists, but it now has a name. This is the first step toward integration.",
            "next_step": f"Consider 'membrane reflect {associated_void.shape_id}' to explore what the silence protects."
            if associated_void
            else None,
        }

        return CommandResult.ok(result)

    async def hold(
        self,
        shape_id: str,
        reason: str = "Productive tension",
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict[str, Any]]:
        """
        Preserve productive tension - prevent premature resolution.

        Usage: kgents membrane hold SHAPE-07 --reason="This drives growth"
        """
        ctx = ctx or CLIContext()

        # Find the shape
        shape = None
        for s in self._shapes:
            if s.shape_id == shape_id or s.shape_id.startswith(shape_id):
                shape = s
                break

        if not shape:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="SHAPE_NOT_FOUND",
                    message=f"Shape not found: {shape_id}",
                )
            )

        # TODO: Persist hold decision via D-gent

        return CommandResult.ok(
            {
                "held": True,
                "shape_id": shape.shape_id,
                "reason": reason,
                "message": "This tension is preserved. It will not trigger interventions.",
            }
        )

    async def release(
        self,
        shape_id: str,
        ctx: CLIContext | None = None,
    ) -> CommandResult[dict[str, Any]]:
        """
        Let go of held tension - allow natural resolution.

        Usage: kgents membrane release SHAPE-03
        """
        ctx = ctx or CLIContext()

        # Find the shape
        shape = None
        for s in self._shapes:
            if s.shape_id == shape_id or s.shape_id.startswith(shape_id):
                shape = s
                break

        if not shape:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.PERMANENT,
                    severity=ErrorSeverity.FAILURE,
                    code="SHAPE_NOT_FOUND",
                    message=f"Shape not found: {shape_id}",
                )
            )

        return CommandResult.ok(
            {
                "released": True,
                "shape_id": shape.shape_id,
                "message": "The tension is released. Natural resolution may now occur.",
            }
        )

    # =========================================================================
    # Shape Detection (Internal)
    # =========================================================================

    async def _detect_shapes(
        self, target: Path, ctx: CLIContext
    ) -> list[SemanticShape]:
        """
        Detect semantic shapes in target.

        Full implementation would use:
        - TDA (Topological Data Analysis) via GUDHI/giotto-tda
        - Embedding models (all-MiniLM-L6-v2)
        - Persistent homology for void detection
        - Mapper algorithm for curvature

        For now, structural heuristics.
        """
        shapes: list[SemanticShape] = []

        # Detect curvature from file clustering
        if target.is_dir():
            # Look for directories with many interconnected files
            py_files = list(target.glob("**/*.py"))
            md_files = list(target.glob("**/*.md"))

            if py_files:
                # Detect curvature around modules with many imports
                shapes.append(
                    SemanticCurvature(
                        shape_id=self._next_shape_id("curvature"),
                        centroid_topic="code_structure",
                        radius=0.5,
                        intensity=min(len(py_files) / 50, 1.0),
                        attractors=("modules", "imports", "dependencies"),
                        repellers=("isolation", "independence"),
                        interpretation=f"Code structure has {len(py_files)} Python files forming a dependency web.",
                    )
                )

            # Detect voids from missing documentation
            if py_files and not md_files:
                shapes.append(
                    SemanticVoid(
                        shape_id=self._next_shape_id("void"),
                        boundary=("code", "implementation", "functions"),
                        depth=0.8,
                        persistence=0.9,
                        interpretation="Documentation void: code exists but documentation is absent.",
                    )
                )

            # Detect dampening around error handling (heuristic)
            shapes.append(
                DampeningField(
                    shape_id=self._next_shape_id("dampening"),
                    trigger="error_handling",
                    compression_ratio=0.3,
                    affected_count=len(py_files),
                    interpretation="Emotional variance may compress around error handling patterns.",
                )
            )

        return shapes

    async def _quick_detect_shapes(self, ctx: CLIContext) -> list[SemanticShape]:
        """Quick shape detection for 'sense' command. Target <100ms."""
        # Just return cached or minimal placeholder
        if self._shapes:
            return self._shapes

        return [
            SemanticCurvature(
                shape_id=self._next_shape_id("curvature"),
                centroid_topic="current_context",
                radius=0.5,
                intensity=0.3,
                attractors=(),
                repellers=(),
                interpretation="Quick sense: run 'observe' for full analysis.",
            )
        ]

    def _generate_suggestion(self, shapes: list[SemanticShape]) -> str:
        """Generate suggestion based on detected shapes."""
        if not shapes:
            return "No significant shapes detected. The manifold appears flat."

        # Find most significant shape
        voids = [s for s in shapes if isinstance(s, SemanticVoid)]
        if voids:
            deepest = max(voids, key=lambda v: v.depth)
            if deepest.depth > 0.7:
                return f"A void around '{', '.join(deepest.boundary[:3])}' is {deepest.depth:.0%} deep. Consider naming what everyone senses but no one says."

        curves = [s for s in shapes if isinstance(s, SemanticCurvature)]
        if curves:
            sharpest = max(curves, key=lambda c: c.intensity)
            if sharpest.intensity > 0.7:
                return f"High curvature around '{sharpest.centroid_topic}' suggests contested concepts. Tension gathers here."

        return (
            "Shapes detected. Use 'touch' to acknowledge, 'name' to voice the unsaid."
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def membrane_observe(
    target_path: str | Path | None = None,
    format: OutputFormat = OutputFormat.RICH,
    budget: BudgetLevel = BudgetLevel.MEDIUM,
) -> CommandResult[MembraneObserveResult]:
    """Convenience function for membrane observe."""
    ctx = CLIContext(
        output_format=format,
        budget=BudgetStatus.from_level(budget),
    )
    cli = MembraneCLI()
    path = Path(target_path).expanduser() if target_path else None
    return await cli.observe(path, ctx)


async def membrane_sense(
    format: OutputFormat = OutputFormat.RICH,
) -> CommandResult[MembraneSenseResult]:
    """Convenience function for membrane sense."""
    ctx = CLIContext(output_format=format)
    cli = MembraneCLI()
    return await cli.sense(ctx)


async def membrane_trace(
    topic: str,
    format: OutputFormat = OutputFormat.RICH,
) -> CommandResult[MembraneTraceResult]:
    """Convenience function for membrane trace."""
    ctx = CLIContext(output_format=format)
    cli = MembraneCLI()
    return await cli.trace(topic, ctx)


# =============================================================================
# Rich Output Formatting
# =============================================================================


def format_membrane_observe_rich(result: MembraneObserveResult) -> str:
    """
    Format MembraneObserveResult as rich terminal output.

    Matches the ephemeral HUD collapse from membrane.md.
    """
    trend_symbol = {"improving": "▵", "stable": "", "declining": "▿"}.get(
        result.trend, ""
    )

    lines = [
        "",
        f"Integrity: {result.integrity_score:.2f} ({trend_symbol} {result.trend})",
        "",
        "Shapes observed:",
    ]

    for shape in result.shapes:
        if isinstance(shape, SemanticVoid):
            lines.append(
                f"  {shape.shape_id}   {', '.join(shape.boundary[:3])} -- {shape.interpretation}"
            )
        elif isinstance(shape, SemanticCurvature):
            lines.append(
                f"  {shape.shape_id}   {shape.centroid_topic} -- {shape.interpretation}"
            )
        elif isinstance(shape, SemanticMomentum):
            lines.append(
                f"  {shape.shape_id}   {shape.topic} -- {shape.interpretation}"
            )
        elif isinstance(shape, DampeningField):
            lines.append(
                f'  {shape.shape_id}   "{shape.trigger}" -- {shape.interpretation}'
            )

    lines.append("")
    lines.append(f"Suggestion: {result.suggestion}")
    lines.append("")

    return "\n".join(lines)
