"""
Psi-gent MetaphorHistorian: N-gent integration for metaphor transformation tracing.

Creates SemanticTraces for Φ/Σ/Φ⁻¹ operations.
Enables forensic analysis when metaphor transformations fail.
"""

from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .types import (
    MetaphorSolution,
    Novel,
    Projection,
    ReifiedSolution,
)


# =============================================================================
# Metaphor Trace Types (aligned with N-gent SemanticTrace)
# =============================================================================


class MetaphorAction:
    """Actions traced by the MetaphorHistorian."""

    PROJECT = "PROJECT"  # Φ: Novel → Projection
    SOLVE = "SOLVE"  # Σ: Projection → MetaphorSolution
    REIFY = "REIFY"  # Φ⁻¹: MetaphorSolution → ReifiedSolution
    VALIDATE = "VALIDATE"  # Axis validation
    BLEND = "BLEND"  # Metaphor blending


@dataclass(frozen=True)
class MetaphorTrace:
    """
    A trace of a metaphor transformation operation.

    Analogous to N-gent's SemanticTrace but specialized
    for Psi-gent operations.
    """

    # Identity
    trace_id: str
    parent_id: str | None
    timestamp: datetime

    # The operation
    action: str
    agent_id: str = "psi"
    agent_genus: str = "Ψ"

    # Input/Output
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] | None = None

    # Reproducibility
    input_hash: str = ""
    input_snapshot: bytes = b""
    output_hash: str | None = None

    # Metrics
    distortion_delta: float = 0.0
    duration_ms: int = 0

    # Classification
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "distortion_delta": self.distortion_delta,
            "success": self.success,
            "error_message": self.error_message,
        }


# =============================================================================
# Tracing Context
# =============================================================================


@dataclass
class TracingContext:
    """Context for a tracing operation."""

    trace_id: str
    parent_id: str | None
    action: str
    start_time: datetime
    input_hash: str
    input_snapshot: bytes


# =============================================================================
# Metaphor Crystal Store
# =============================================================================


@dataclass
class MetaphorCrystalStore:
    """
    Storage for metaphor transformation traces.

    Simplified in-memory store; can be replaced with D-gent backend.
    """

    _traces: list[MetaphorTrace] = field(default_factory=list)
    _by_id: dict[str, MetaphorTrace] = field(default_factory=dict)

    def store(self, trace: MetaphorTrace) -> None:
        """Store a trace."""
        self._traces.append(trace)
        self._by_id[trace.trace_id] = trace

    def get(self, trace_id: str) -> MetaphorTrace | None:
        """Get a trace by ID."""
        return self._by_id.get(trace_id)

    def get_by_action(self, action: str) -> list[MetaphorTrace]:
        """Get all traces for an action."""
        return [t for t in self._traces if t.action == action]

    def get_failed(self) -> list[MetaphorTrace]:
        """Get all failed traces."""
        return [t for t in self._traces if not t.success]

    def get_high_distortion(self, threshold: float = 0.5) -> list[MetaphorTrace]:
        """Get traces with high distortion."""
        return [t for t in self._traces if t.distortion_delta > threshold]

    def get_chain(self, trace_id: str) -> list[MetaphorTrace]:
        """Get the chain of traces leading to this one."""
        chain = []
        current_id: str | None = trace_id
        while current_id:
            trace = self.get(current_id)
            if trace:
                chain.append(trace)
                current_id = trace.parent_id
            else:
                break
        return list(reversed(chain))

    def clear(self) -> None:
        """Clear all traces."""
        self._traces.clear()
        self._by_id.clear()


# =============================================================================
# Metaphor Historian
# =============================================================================


@dataclass
class MetaphorHistorian:
    """
    Invisible recorder of metaphor transformations.

    Creates SemanticTraces for:
    - Φ (project): Problem → Metaphor mapping
    - Σ (solve): Solution in metaphor space
    - Φ⁻¹ (reify): Metaphor → Reality translation
    """

    store: MetaphorCrystalStore = field(default_factory=MetaphorCrystalStore)
    _active_contexts: dict[str, TracingContext] = field(default_factory=dict)

    def begin_trace(
        self, action: str, input_obj: Any, parent_id: str | None = None
    ) -> TracingContext:
        """
        Start recording a transformation.

        Returns context for completing the trace.
        """
        trace_id = str(uuid4())

        # Serialize input for reproducibility
        try:
            input_snapshot = pickle.dumps(input_obj)
        except Exception:
            input_snapshot = b""

        # Hash for deduplication
        input_hash = hashlib.sha256(input_snapshot).hexdigest()[:16]

        ctx = TracingContext(
            trace_id=trace_id,
            parent_id=parent_id,
            action=action,
            start_time=datetime.now(),
            input_hash=input_hash,
            input_snapshot=input_snapshot,
        )

        self._active_contexts[trace_id] = ctx
        return ctx

    def end_trace(
        self,
        ctx: TracingContext,
        outputs: dict[str, Any],
        distortion_delta: float = 0.0,
        success: bool = True,
        error_message: str = "",
    ) -> MetaphorTrace:
        """
        Complete a trace with outputs.
        """
        duration = int((datetime.now() - ctx.start_time).total_seconds() * 1000)

        # Hash output
        try:
            output_hash = hashlib.sha256(pickle.dumps(outputs)).hexdigest()[:16]
        except Exception:
            output_hash = None

        trace = MetaphorTrace(
            trace_id=ctx.trace_id,
            parent_id=ctx.parent_id,
            timestamp=ctx.start_time,
            action=ctx.action,
            inputs=self._summarize_inputs(ctx.input_snapshot),
            outputs=outputs,
            input_hash=ctx.input_hash,
            input_snapshot=ctx.input_snapshot,
            output_hash=output_hash,
            distortion_delta=distortion_delta,
            duration_ms=duration,
            success=success,
            error_message=error_message,
        )

        self.store.store(trace)
        del self._active_contexts[ctx.trace_id]

        return trace

    def abort_trace(self, ctx: TracingContext, error: str) -> MetaphorTrace:
        """Abort a trace with error."""
        return self.end_trace(
            ctx, outputs={}, distortion_delta=1.0, success=False, error_message=error
        )

    def trace_projection(
        self, problem: Novel, projection: Projection, parent_id: str | None = None
    ) -> MetaphorTrace:
        """
        Record a projection (Φ) operation.
        """
        ctx = self.begin_trace(MetaphorAction.PROJECT, problem, parent_id)
        return self.end_trace(
            ctx,
            outputs={
                "metaphor_id": projection.target.metaphor_id,
                "metaphor_name": projection.target.name,
                "mapped_concepts": len(projection.mapped_concepts),
                "confidence": projection.confidence,
                "coverage": projection.coverage,
            },
            distortion_delta=0.0,  # Distortion calculated at reify
        )

    def trace_solution(
        self, solution: MetaphorSolution, parent_id: str | None = None
    ) -> MetaphorTrace:
        """
        Record a solve (Σ) operation.
        """
        ctx = self.begin_trace(MetaphorAction.SOLVE, solution.projection, parent_id)
        return self.end_trace(
            ctx,
            outputs={
                "operations_applied": list(solution.operations_applied),
                "confidence": solution.confidence,
                "completeness": solution.completeness,
            },
        )

    def trace_reification(
        self, reified: ReifiedSolution, parent_id: str | None = None
    ) -> MetaphorTrace:
        """
        Record a reification (Φ⁻¹) operation.
        """
        ctx = self.begin_trace(
            MetaphorAction.REIFY, reified.metaphor_solution, parent_id
        )
        return self.end_trace(
            ctx,
            outputs={
                "problem_id": reified.original_problem.problem_id,
                "quality": reified.overall_quality,
                "successful": reified.is_successful,
            },
            distortion_delta=reified.distortion.delta,
            success=reified.is_successful,
        )

    def _summarize_inputs(self, snapshot: bytes) -> dict[str, Any]:
        """Summarize inputs from snapshot."""
        if not snapshot:
            return {}
        try:
            obj = pickle.loads(snapshot)
            if hasattr(obj, "__dict__"):
                return {
                    "type": type(obj).__name__,
                    "keys": list(obj.__dict__.keys())[:5],
                }
            return {"type": type(obj).__name__}
        except Exception:
            return {"type": "unknown", "size": len(snapshot)}


# =============================================================================
# Forensic Bard (for diagnosing failures)
# =============================================================================


@dataclass(frozen=True)
class MetaphorDiagnosis:
    """Diagnosis of a metaphor transformation failure."""

    narrative: str
    failure_type: str
    traces_examined: int
    root_cause: str
    suggested_metaphors: tuple[str, ...]
    anti_patterns_detected: tuple[str, ...]


class ForensicBard:
    """
    Detective specializing in metaphor failures.

    Analyzes trace chains to diagnose why transformations failed.
    """

    def diagnose_failure(
        self, historian: MetaphorHistorian, trace_id: str
    ) -> MetaphorDiagnosis:
        """
        Diagnose a failed transformation.
        """
        chain = historian.store.get_chain(trace_id)
        if not chain:
            return MetaphorDiagnosis(
                narrative="No traces found for the given ID.",
                failure_type="unknown",
                traces_examined=0,
                root_cause="Trace not found",
                suggested_metaphors=(),
                anti_patterns_detected=(),
            )

        # Analyze the chain
        failure_type = self._classify_failure(chain)
        root_cause = self._find_root_cause(chain)
        anti_patterns = self._detect_anti_patterns(chain)
        narrative = self._build_narrative(chain, failure_type, root_cause)

        return MetaphorDiagnosis(
            narrative=narrative,
            failure_type=failure_type,
            traces_examined=len(chain),
            root_cause=root_cause,
            suggested_metaphors=self._suggest_alternatives(chain),
            anti_patterns_detected=tuple(anti_patterns),
        )

    def diagnose_high_distortion(
        self, historian: MetaphorHistorian, threshold: float = 0.5
    ) -> list[MetaphorDiagnosis]:
        """
        Diagnose all high-distortion transformations.
        """
        high_distortion = historian.store.get_high_distortion(threshold)
        return [
            self.diagnose_failure(historian, trace.trace_id)
            for trace in high_distortion
        ]

    def _classify_failure(self, chain: list[MetaphorTrace]) -> str:
        """Classify the type of failure."""
        failed = [t for t in chain if not t.success]
        if not failed:
            # Not a failure, just high distortion
            high_dist = [t for t in chain if t.distortion_delta > 0.5]
            if high_dist:
                return "high_distortion"
            return "success"

        # Find first failure
        first_fail = failed[0]
        if first_fail.action == MetaphorAction.PROJECT:
            return "projection_failure"
        elif first_fail.action == MetaphorAction.SOLVE:
            return "solution_failure"
        elif first_fail.action == MetaphorAction.REIFY:
            return "reification_failure"
        return "unknown_failure"

    def _find_root_cause(self, chain: list[MetaphorTrace]) -> str:
        """Find the root cause of failure."""
        for trace in chain:
            if not trace.success:
                return trace.error_message or f"Failed at {trace.action}"
            if trace.distortion_delta > 0.7:
                return (
                    f"High distortion ({trace.distortion_delta:.2f}) at {trace.action}"
                )
        return "No clear root cause identified"

    def _detect_anti_patterns(self, chain: list[MetaphorTrace]) -> list[str]:
        """Detect anti-patterns in the transformation chain."""
        patterns = []

        # Check for Procrustean bed
        project_traces = [t for t in chain if t.action == MetaphorAction.PROJECT]
        for t in project_traces:
            if t.outputs and t.outputs.get("coverage", 0) < 0.3:
                patterns.append("procrustean_bed")
                break

        # Check for high distortion (map-territory confusion risk)
        high_dist = [t for t in chain if t.distortion_delta > 0.5]
        if high_dist:
            patterns.append("high_distortion_risk")

        return patterns

    def _suggest_alternatives(self, chain: list[MetaphorTrace]) -> tuple[str, ...]:
        """Suggest alternative metaphors based on failure analysis."""
        suggestions = []

        # If projection failed, suggest more generic metaphors
        project_fails = [
            t
            for t in chain
            if t.action == MetaphorAction.PROJECT
            and (not t.success or t.outputs.get("coverage", 0) < 0.4)
        ]
        if project_fails:
            suggestions.append("hero_journey")  # More generic
            suggestions.append("ecosystem")  # Broad applicability

        return tuple(suggestions)

    def _build_narrative(
        self, chain: list[MetaphorTrace], failure_type: str, root_cause: str
    ) -> str:
        """Build a narrative of what happened."""
        lines = [
            "=== Metaphor Transformation Forensics ===",
            "",
            f"Failure Type: {failure_type}",
            f"Root Cause: {root_cause}",
            "",
            "Timeline:",
        ]

        for i, trace in enumerate(chain, 1):
            status = "✓" if trace.success else "✗"
            distortion = (
                f" (Δ={trace.distortion_delta:.2f})"
                if trace.distortion_delta > 0
                else ""
            )
            lines.append(f"  {i}. [{status}] {trace.action}{distortion}")
            if trace.outputs:
                for key, value in list(trace.outputs.items())[:3]:
                    lines.append(f"      - {key}: {value}")

        lines.append("")
        lines.append(f"Examined {len(chain)} trace(s)")

        return "\n".join(lines)
