"""
Psi-gent PsychopompAgent: The Universal Translator of Semantic Topologies.

Main orchestrator composing:
- HolographicMetaphorLibrary (M-gent memory)
- MorphicFunctor (Φ/Φ⁻¹ transformations)
- 4-Axis Tensor (Z/X/Y/T validation)
- MetaphorHistorian (N-gent tracing)
- MetaphorUmwelt (agent-specific projection)
- MetaphorEvolutionAgent (E-gent learning)

The Psychopomp guides problems from the Novel (unknown) to the Archetype (known).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .types import (
    AntiPattern,
    AntiPatternDetection,
    Distortion,
    Metaphor,
    MetaphorSolution,
    Novel,
    Projection,
    ReifiedSolution,
    StabilityStatus,
    TensorPosition,
    TensorValidation,
)
from .morphic_functor import MorphicFunctor
from .metaphor_library import WeightedMetaphor
from .holographic_library import HolographicMetaphorLibrary
from .resolution_scaler import ResolutionScaler
from .dialectical_rotator import DialecticalRotator
from .topological_validator import TopologicalValidator
from .axiological_exchange import AxiologicalExchange
from .metaphor_historian import MetaphorHistorian
from .metaphor_umwelt import MetaphorUmwelt, create_neutral_umwelt


# =============================================================================
# Psychopomp Configuration
# =============================================================================


@dataclass(frozen=True)
class PsychopompConfig:
    """Configuration for the Psychopomp agent."""

    # Search parameters
    max_metaphor_candidates: int = 5
    max_iterations: int = 3
    distortion_threshold: float = 0.5

    # Tensor thresholds
    z_axis_threshold: float = 0.5  # MHC resolution
    x_axis_threshold: float = 0.4  # Shadow safety
    y_axis_threshold: float = 0.5  # Topological integrity
    t_axis_threshold: float = 0.5  # Axiological cost

    # Learning
    enable_learning: bool = True
    enable_tracing: bool = True


# =============================================================================
# Search State
# =============================================================================


class SearchPhase(Enum):
    """Phases of the metaphor search process."""

    FETCH = "fetch"  # Fetch candidates from library
    PROJECT = "project"  # Φ: project problem
    VALIDATE = "validate"  # 4-axis tensor validation
    SOLVE = "solve"  # Σ: solve in metaphor space
    REIFY = "reify"  # Φ⁻¹: translate back
    COMPLETE = "complete"  # Success
    FAILED = "failed"  # No solution found


@dataclass
class SearchState:
    """State of the metaphor search process."""

    problem: Novel
    phase: SearchPhase
    iteration: int = 0

    # Candidates
    candidates: list[WeightedMetaphor] = field(default_factory=list)
    current_candidate_idx: int = 0

    # Best results
    best_projection: Projection | None = None
    best_solution: MetaphorSolution | None = None
    best_reified: ReifiedSolution | None = None

    # Validation results
    tensor_validations: list[TensorValidation] = field(default_factory=list)

    # Trace chain
    trace_ids: list[str] = field(default_factory=list)


# =============================================================================
# Search Result
# =============================================================================


@dataclass(frozen=True)
class PsychopompResult:
    """Result from a Psychopomp search."""

    success: bool
    problem: Novel
    reified_solution: ReifiedSolution | None = None
    metaphor_used: Metaphor | None = None
    tensor_position: TensorPosition | None = None
    distortion: Distortion | None = None
    iterations: int = 0
    trace_id: str | None = None

    # Diagnostics
    candidates_tried: int = 0
    anti_patterns_detected: tuple[AntiPatternDetection, ...] = ()
    failure_reason: str = ""


# =============================================================================
# Psychopomp Agent
# =============================================================================


@dataclass
class PsychopompAgent:
    """
    The Universal Translator of Semantic Topologies.

    Guides problems from Novel (unknown) through Metaphor to Archetype (known).

    Pipeline:
    1. Fetch candidates (via Umwelt lens)
    2. Project problem (Φ)
    3. Validate (4-axis tensor)
    4. Solve in metaphor space (Σ)
    5. Reify back to problem space (Φ⁻¹)
    6. Learn from outcome
    """

    # Core components
    library: HolographicMetaphorLibrary = field(
        default_factory=HolographicMetaphorLibrary
    )
    functor: MorphicFunctor = field(default_factory=MorphicFunctor)

    # 4-axis validators
    z_axis: ResolutionScaler = field(default_factory=ResolutionScaler)
    x_axis: DialecticalRotator = field(default_factory=DialecticalRotator)
    y_axis: TopologicalValidator = field(default_factory=TopologicalValidator)
    t_axis: AxiologicalExchange = field(default_factory=AxiologicalExchange)

    # N-gent integration
    historian: MetaphorHistorian = field(default_factory=MetaphorHistorian)

    # Umwelt (agent-specific projection)
    umwelt: MetaphorUmwelt = field(default_factory=create_neutral_umwelt)

    # Configuration
    config: PsychopompConfig = field(default_factory=PsychopompConfig)

    def __post_init__(self):
        # Bind library to umwelt
        self.umwelt.bind_library(self.library)

    def solve(self, problem: Novel) -> PsychopompResult:
        """
        Main entry point: solve a novel problem via metaphor.

        Returns a PsychopompResult with the solution or failure diagnostics.
        """
        # Initialize search state
        state = SearchState(problem=problem, phase=SearchPhase.FETCH)

        # Begin trace
        trace_id = None
        if self.config.enable_tracing:
            ctx = self.historian.begin_trace(
                action="PSYCHOPOMP_SOLVE",
                input_obj=problem,
            )
            trace_id = ctx.trace_id
            state.trace_ids.append(trace_id)

        # Run search loop
        result = self._search_loop(state)

        # Complete trace
        if self.config.enable_tracing and trace_id:
            self.historian.end_trace(
                ctx,
                outputs={
                    "success": result.success,
                    "metaphor": result.metaphor_used.metaphor_id
                    if result.metaphor_used
                    else None,
                    "iterations": result.iterations,
                },
                success=result.success,
            )

        # Learn from outcome
        if self.config.enable_learning and result.metaphor_used:
            self.library.update_usage(
                result.metaphor_used.metaphor_id, success=result.success
            )

        return result

    def _search_loop(self, state: SearchState) -> PsychopompResult:
        """The main search loop through metaphor space."""
        anti_patterns: list[AntiPatternDetection] = []

        while state.iteration < self.config.max_iterations:
            state.iteration += 1

            # Phase 1: Fetch candidates
            if state.phase == SearchPhase.FETCH:
                state.candidates = self._fetch_candidates(state.problem)
                if not state.candidates:
                    return self._failure_result(
                        state, "No metaphor candidates found", anti_patterns
                    )
                state.phase = SearchPhase.PROJECT

            # Phase 2: Project problem into metaphor space
            if state.phase == SearchPhase.PROJECT:
                candidate = state.candidates[state.current_candidate_idx]

                # Check if umwelt allows this metaphor
                if not self.umwelt.can_use(candidate.metaphor):
                    state.current_candidate_idx += 1
                    if state.current_candidate_idx >= len(state.candidates):
                        return self._failure_result(
                            state,
                            "No metaphors passed umwelt constraints",
                            anti_patterns,
                        )
                    continue

                projection = self.functor.project(state.problem, candidate.metaphor)
                state.best_projection = projection

                # Trace projection
                if self.config.enable_tracing:
                    trace = self.historian.trace_projection(
                        state.problem,
                        projection,
                        parent_id=state.trace_ids[-1] if state.trace_ids else None,
                    )
                    state.trace_ids.append(trace.trace_id)

                state.phase = SearchPhase.VALIDATE

            # Phase 3: Validate via 4-axis tensor
            if state.phase == SearchPhase.VALIDATE:
                projection = state.best_projection
                if not projection:
                    state.phase = SearchPhase.PROJECT
                    continue

                distortion = self.functor.calculate_distortion(
                    state.problem, projection
                )

                validation = self._validate_tensor(projection, distortion)
                state.tensor_validations.append(validation)

                # Collect anti-pattern detections
                anti_patterns.extend(self._detect_anti_patterns(projection, distortion))

                if validation.overall_status == StabilityStatus.STABLE:
                    state.phase = SearchPhase.SOLVE
                elif validation.overall_status == StabilityStatus.FRAGILE:
                    # Fragile is acceptable, proceed with caution
                    state.phase = SearchPhase.SOLVE
                else:
                    # Unstable - try next candidate
                    state.current_candidate_idx += 1
                    if state.current_candidate_idx >= len(state.candidates):
                        return self._failure_result(
                            state, "All candidates failed validation", anti_patterns
                        )
                    state.phase = SearchPhase.PROJECT

            # Phase 4: Solve in metaphor space
            if state.phase == SearchPhase.SOLVE:
                projection = state.best_projection
                if not projection:
                    state.phase = SearchPhase.PROJECT
                    continue

                solution = self._solve_in_metaphor_space(projection)
                state.best_solution = solution

                # Trace solution
                if self.config.enable_tracing:
                    trace = self.historian.trace_solution(
                        solution,
                        parent_id=state.trace_ids[-1] if state.trace_ids else None,
                    )
                    state.trace_ids.append(trace.trace_id)

                state.phase = SearchPhase.REIFY

            # Phase 5: Reify back to problem space
            if state.phase == SearchPhase.REIFY:
                solution = state.best_solution
                projection = state.best_projection
                if not solution or not projection:
                    state.phase = SearchPhase.SOLVE
                    continue

                reified = self.functor.reify(solution, state.problem, projection)
                state.best_reified = reified

                # Trace reification
                if self.config.enable_tracing:
                    trace = self.historian.trace_reification(
                        reified,
                        parent_id=state.trace_ids[-1] if state.trace_ids else None,
                    )
                    state.trace_ids.append(trace.trace_id)

                # Check if successful
                if reified.is_successful:
                    state.phase = SearchPhase.COMPLETE
                else:
                    # Try next candidate
                    state.current_candidate_idx += 1
                    if state.current_candidate_idx >= len(state.candidates):
                        return self._failure_result(
                            state,
                            "Reification failed for all candidates",
                            anti_patterns,
                        )
                    state.phase = SearchPhase.PROJECT

            # Phase 6: Complete
            if state.phase == SearchPhase.COMPLETE:
                return self._success_result(state, anti_patterns)

        # Exceeded max iterations
        return self._failure_result(
            state,
            f"Exceeded max iterations ({self.config.max_iterations})",
            anti_patterns,
        )

    def _fetch_candidates(self, problem: Novel) -> list[WeightedMetaphor]:
        """Fetch metaphor candidates through the umwelt lens."""
        return self.umwelt.project(problem, limit=self.config.max_metaphor_candidates)

    def _validate_tensor(
        self, projection: Projection, distortion: Distortion
    ) -> TensorValidation:
        """Validate projection across all 4 axes."""
        # Z-axis: MHC resolution
        z_result = self.z_axis.validate(
            projection.source, projection.target.tractability
        )

        # X-axis: Shadow safety
        x_result = self.x_axis.validate(projection)

        # Y-axis: Topological integrity
        y_result = self.y_axis.validate(projection)

        # T-axis: Axiological cost
        t_result = self.t_axis.validate(projection, distortion)

        # Calculate overall status
        results = [z_result, x_result, y_result, t_result]
        if all(r.status == StabilityStatus.STABLE for r in results):
            overall = StabilityStatus.STABLE
        elif any(r.status == StabilityStatus.UNSTABLE for r in results):
            overall = StabilityStatus.UNSTABLE
        else:
            overall = StabilityStatus.FRAGILE

        # Calculate position
        position = TensorPosition(
            z_altitude=z_result.score,
            x_rotation=x_result.score,
            y_topology=y_result.score,
            t_axiological=t_result.score,
        )

        return TensorValidation(
            position=position,
            z_result=z_result,
            x_result=x_result,
            y_result=y_result,
            t_result=t_result,
            overall_status=overall,
            overall_confidence=sum(r.score for r in results) / 4,
        )

    def _detect_anti_patterns(
        self, projection: Projection, distortion: Distortion
    ) -> list[AntiPatternDetection]:
        """Detect anti-patterns across all validators."""
        detections = []

        # X-axis: Shadow blindness
        shadow_detection = self.x_axis.detect_shadow_blindness(projection)
        if shadow_detection.detected:
            detections.append(shadow_detection)

        # Y-axis: Map-territory confusion
        map_confusion = self.y_axis.detect_map_territory_confusion(projection)
        if map_confusion.detected:
            detections.append(map_confusion)

        # T-axis: Value blindness
        value_blindness = self.t_axis.detect_value_blindness(projection, distortion)
        if value_blindness.detected:
            detections.append(value_blindness)

        # Check for procrustean bed (forced fit)
        if projection.coverage < 0.3 and projection.confidence > 0.7:
            detections.append(
                AntiPatternDetection(
                    pattern=AntiPattern.PROCRUSTEAN_BED,
                    detected=True,
                    confidence=0.7,
                    evidence=f"Low coverage ({projection.coverage:.2f}) with high confidence ({projection.confidence:.2f})",
                    mitigation="Try a more general metaphor or break problem into sub-problems",
                )
            )

        return detections

    def _solve_in_metaphor_space(self, projection: Projection) -> MetaphorSolution:
        """Solve the projected problem in metaphor space."""
        # Apply metaphor operations
        operations_applied = []
        intermediate_results = []

        for op in projection.applicable_operations:
            operations_applied.append(op.name)
            intermediate_results.append(f"Applied {op.name}: {op.description}")

        # Calculate confidence based on operation coverage
        confidence = len(operations_applied) / max(len(projection.target.operations), 1)

        return MetaphorSolution(
            projection=projection,
            operations_applied=tuple(operations_applied),
            intermediate_results=tuple(intermediate_results),
            final_state=f"Solved via {projection.target.name}",
            confidence=confidence,
            completeness=projection.coverage,
        )

    def _success_result(
        self, state: SearchState, anti_patterns: list[AntiPatternDetection]
    ) -> PsychopompResult:
        """Build a success result."""
        reified = state.best_reified
        projection = state.best_projection

        return PsychopompResult(
            success=True,
            problem=state.problem,
            reified_solution=reified,
            metaphor_used=projection.target if projection else None,
            tensor_position=state.tensor_validations[-1].position
            if state.tensor_validations
            else None,
            distortion=reified.distortion if reified else None,
            iterations=state.iteration,
            trace_id=state.trace_ids[0] if state.trace_ids else None,
            candidates_tried=state.current_candidate_idx + 1,
            anti_patterns_detected=tuple(anti_patterns),
        )

    def _failure_result(
        self,
        state: SearchState,
        reason: str,
        anti_patterns: list[AntiPatternDetection],
    ) -> PsychopompResult:
        """Build a failure result."""
        return PsychopompResult(
            success=False,
            problem=state.problem,
            iterations=state.iteration,
            trace_id=state.trace_ids[0] if state.trace_ids else None,
            candidates_tried=state.current_candidate_idx + 1,
            anti_patterns_detected=tuple(anti_patterns),
            failure_reason=reason,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_psychopomp(
    umwelt: MetaphorUmwelt | None = None,
    config: PsychopompConfig | None = None,
) -> PsychopompAgent:
    """Create a Psychopomp agent with optional customization."""
    agent = PsychopompAgent(
        config=config or PsychopompConfig(),
    )
    if umwelt:
        agent.umwelt = umwelt
        umwelt.bind_library(agent.library)
    return agent


def solve_problem(
    problem: Novel,
    umwelt: MetaphorUmwelt | None = None,
) -> PsychopompResult:
    """Convenience function to solve a problem via metaphor."""
    agent = create_psychopomp(umwelt=umwelt)
    return agent.solve(problem)
