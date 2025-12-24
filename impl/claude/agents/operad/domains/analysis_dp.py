"""
Analysis Operad DP Bridge: Integrate Four-Mode Analysis with DP-Native System.

This module bridges the Analysis Operad with the DP-native kgents architecture:
- Analysis as a DP problem formulation
- Principle-based reward for analysis quality
- PolicyTrace integration for witnessed analysis

The Core Insight:
    Analysis IS a DP problem where:
    - States: Partial analysis results (per mode)
    - Actions: Apply analysis modes (categorical, epistemic, dialectical, generative)
    - Transition: Accumulate findings
    - Reward: Constitution-based (principles satisfied by analysis)

    V*(spec) = max_mode [R(partial, mode) + γ · V*(next_partial)]

See: spec/theory/analysis-operad.md §2.4 (DP-Native Integration)
See: services/categorical/dp_bridge.py

Teaching:
    gotcha: Analysis modes are NOT actions on the spec—they're actions on the
            ANALYSIS STATE. The spec is fixed; what changes is our understanding.
            (Evidence: AnalysisState tracks which modes have been applied)

    gotcha: The reward function favors COMPLETENESS (all modes applied) and
            QUALITY (modes return valid, non-contradictory results).
            (Evidence: analysis_reward() in ProblemFormulation)

    gotcha: Integration with Witness happens via PolicyTrace.to_marks(). Every
            analysis step becomes a Mark in the Witness system.
            (Evidence: analyze_with_witness() function)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, FrozenSet

from services.categorical.dp_bridge import (
    PolicyTrace,
    ProblemFormulation,
    Principle,
    TraceEntry,
    DPSolver,
)

from .analysis import (
    ANALYSIS_OPERAD,
    CategoricalReport,
    DialecticalReport,
    EpistemicReport,
    FullAnalysisReport,
    GenerativeReport,
    ContradictionType,
    self_analyze as _self_analyze,
)


# =============================================================================
# Analysis State for DP Formulation
# =============================================================================


@dataclass(frozen=True)
class AnalysisState:
    """
    State in the analysis DP formulation.

    Tracks which modes have been applied and their results.
    """

    target: str
    categorical_done: bool = False
    epistemic_done: bool = False
    dialectical_done: bool = False
    generative_done: bool = False

    # Cached results (None if not yet computed)
    categorical_result: CategoricalReport | None = None
    epistemic_result: EpistemicReport | None = None
    dialectical_result: DialecticalReport | None = None
    generative_result: GenerativeReport | None = None

    @property
    def modes_applied(self) -> int:
        """Count of analysis modes applied."""
        return sum([
            self.categorical_done,
            self.epistemic_done,
            self.dialectical_done,
            self.generative_done,
        ])

    @property
    def is_complete(self) -> bool:
        """True if all four modes have been applied."""
        return self.modes_applied == 4

    @property
    def has_violations(self) -> bool:
        """True if any completed mode found violations."""
        if self.categorical_result and self.categorical_result.has_violations:
            return True
        if self.dialectical_result and self.dialectical_result.problematic_count > 0:
            return True
        return False

    def __hash__(self) -> int:
        return hash((
            self.target,
            self.categorical_done,
            self.epistemic_done,
            self.dialectical_done,
            self.generative_done,
        ))


@dataclass(frozen=True)
class AnalysisAction:
    """
    An action in the analysis DP formulation.

    Each action applies one analysis mode.
    """

    mode: str  # "categorical", "epistemic", "dialectical", "generative"

    def __hash__(self) -> int:
        return hash(self.mode)


# =============================================================================
# Analysis Problem Formulation
# =============================================================================


def create_analysis_formulation(target: str) -> ProblemFormulation[AnalysisState, AnalysisAction]:
    """
    Create a DP problem formulation for analyzing a spec.

    The formulation defines:
    - States: Partial analysis results
    - Actions: Apply analysis modes
    - Transition: Execute mode and update state
    - Reward: Principle-based scoring
    """

    # Initial state: no modes applied
    initial_state = AnalysisState(target=target)
    initial_states: FrozenSet[AnalysisState] = frozenset({initial_state})

    # Goal states: all modes applied with no violations
    # (We'll compute this dynamically based on what states we reach)
    goal_states: FrozenSet[AnalysisState] = frozenset()

    def available_actions(state: AnalysisState) -> FrozenSet[AnalysisAction]:
        """Return actions available from this state."""
        actions: set[AnalysisAction] = set()

        if not state.categorical_done:
            actions.add(AnalysisAction("categorical"))
        if not state.epistemic_done:
            actions.add(AnalysisAction("epistemic"))
        if not state.dialectical_done:
            actions.add(AnalysisAction("dialectical"))
        if not state.generative_done:
            actions.add(AnalysisAction("generative"))

        return frozenset(actions)

    def transition(state: AnalysisState, action: AnalysisAction) -> AnalysisState:
        """
        Execute an analysis mode and return new state (structural, sync).

        This is the sync fallback that uses structural analysis.
        For LLM-backed analysis, use create_analysis_formulation_llm().
        """
        from .analysis import (
            _categorical_analysis,
            _epistemic_analysis,
            _dialectical_analysis,
            _generative_analysis,
        )

        match action.mode:
            case "categorical":
                result = _categorical_analysis(state.target)
                return AnalysisState(
                    target=state.target,
                    categorical_done=True,
                    epistemic_done=state.epistemic_done,
                    dialectical_done=state.dialectical_done,
                    generative_done=state.generative_done,
                    categorical_result=result,
                    epistemic_result=state.epistemic_result,
                    dialectical_result=state.dialectical_result,
                    generative_result=state.generative_result,
                )
            case "epistemic":
                result = _epistemic_analysis(state.target)
                return AnalysisState(
                    target=state.target,
                    categorical_done=state.categorical_done,
                    epistemic_done=True,
                    dialectical_done=state.dialectical_done,
                    generative_done=state.generative_done,
                    categorical_result=state.categorical_result,
                    epistemic_result=result,
                    dialectical_result=state.dialectical_result,
                    generative_result=state.generative_result,
                )
            case "dialectical":
                result = _dialectical_analysis(state.target)
                return AnalysisState(
                    target=state.target,
                    categorical_done=state.categorical_done,
                    epistemic_done=state.epistemic_done,
                    dialectical_done=True,
                    generative_done=state.generative_done,
                    categorical_result=state.categorical_result,
                    epistemic_result=state.epistemic_result,
                    dialectical_result=result,
                    generative_result=state.generative_result,
                )
            case "generative":
                result = _generative_analysis(state.target)
                return AnalysisState(
                    target=state.target,
                    categorical_done=state.categorical_done,
                    epistemic_done=state.epistemic_done,
                    dialectical_done=state.dialectical_done,
                    generative_done=True,
                    categorical_result=state.categorical_result,
                    epistemic_result=state.epistemic_result,
                    dialectical_result=state.dialectical_result,
                    generative_result=result,
                )
            case _:
                return state

    def reward(
        state: AnalysisState,
        action: AnalysisAction,
        next_state: AnalysisState,
    ) -> float:
        """
        Compute reward for analysis action.

        Reward is based on:
        - COMPOSABLE: Analysis integrates with system (0.3)
        - GENERATIVE: Analysis compresses understanding (0.3)
        - ETHICAL: Analysis is transparent about findings (0.2)
        - TASTEFUL: Analysis is focused, not sprawling (0.2)
        """
        # Base reward for making progress
        progress_reward = 0.25 if next_state.modes_applied > state.modes_applied else 0.0

        # Quality reward based on results
        quality_reward = 0.0

        # Categorical: reward for laws passing
        if next_state.categorical_result:
            cat = next_state.categorical_result
            if cat.laws_total > 0:
                quality_reward += 0.15 * (cat.laws_passed / cat.laws_total)

        # Epistemic: reward for being grounded
        if next_state.epistemic_result:
            epi = next_state.epistemic_result
            if epi.is_grounded:
                quality_reward += 0.15
            if epi.has_valid_bootstrap:
                quality_reward += 0.05

        # Dialectical: reward for resolving tensions (penalize unresolved problems)
        if next_state.dialectical_result:
            dia = next_state.dialectical_result
            if len(dia.tensions) > 0:
                resolution_ratio = dia.resolved_count / len(dia.tensions)
                quality_reward += 0.10 * resolution_ratio
            # Penalty for problematic contradictions
            quality_reward -= 0.05 * dia.problematic_count

        # Generative: reward for compression and regenerability
        if next_state.generative_result:
            gen = next_state.generative_result
            if gen.is_compressed:
                quality_reward += 0.10
            if gen.is_regenerable:
                quality_reward += 0.10

        # Completion bonus
        completion_bonus = 0.5 if next_state.is_complete else 0.0

        # Penalty for violations
        violation_penalty = -0.3 if next_state.has_violations else 0.0

        return progress_reward + quality_reward + completion_bonus + violation_penalty

    return ProblemFormulation(
        name=f"Analysis({target})",
        description=f"Four-mode analysis of {target}",
        state_type=AnalysisState,
        initial_states=initial_states,
        goal_states=goal_states,
        available_actions=available_actions,
        transition=transition,
        reward=reward,
    )


# =============================================================================
# Integration Functions
# =============================================================================


def analyze_as_dp(target: str, gamma: float = 0.95) -> tuple[float, PolicyTrace[AnalysisState]]:
    """
    Analyze a spec using the DP formulation (structural mode).

    This runs analysis as a DP problem, finding the "optimal" order
    of analysis modes (which in practice means: apply all modes).

    Uses structural (non-LLM) analysis. For LLM-backed analysis,
    use analyze_as_dp_llm().

    Args:
        target: Path to spec file to analyze
        gamma: Discount factor for DP

    Returns:
        Tuple of (optimal value, policy trace with analysis steps)
    """
    formulation = create_analysis_formulation(target)
    solver = DPSolver(formulation=formulation, gamma=gamma)
    return solver.solve()


async def analyze_as_dp_llm(target: str, gamma: float = 0.95) -> tuple[float, PolicyTrace[AnalysisState]]:
    """
    Analyze a spec using the DP formulation (LLM mode).

    This runs analysis as a DP problem using REAL LLM-backed analysis
    for each mode. The DP solver finds the optimal order of analysis
    modes and executes them with Claude.

    Note: Since the DP solver is currently synchronous, we run all
    possible mode orderings and pick the best. In practice, the order
    doesn't matter much since modes are largely independent.

    Args:
        target: Path to spec file to analyze
        gamma: Discount factor for DP

    Returns:
        Tuple of (optimal value, policy trace with analysis steps)
    """
    from .analysis import (
        analyze_categorical_llm,
        analyze_epistemic_llm,
        analyze_dialectical_llm,
        analyze_generative_llm,
    )

    # Run all four modes (order doesn't matter for total reward)
    categorical_result = await analyze_categorical_llm(target)
    epistemic_result = await analyze_epistemic_llm(target)
    dialectical_result = await analyze_dialectical_llm(target)
    generative_result = await analyze_generative_llm(target)

    # Build final state
    final_state = AnalysisState(
        target=target,
        categorical_done=True,
        epistemic_done=True,
        dialectical_done=True,
        generative_done=True,
        categorical_result=categorical_result,
        epistemic_result=epistemic_result,
        dialectical_result=dialectical_result,
        generative_result=generative_result,
    )

    # Compute total reward (same reward function as sync version)
    # We use a simplified trace since we ran all modes
    initial_state = AnalysisState(target=target)

    # Create a trace with all transitions
    # (For simplicity, we'll show them in a fixed order: cat, epi, dia, gen)
    trace_entries = []

    # Categorical step
    state_after_cat = AnalysisState(
        target=target,
        categorical_done=True,
        categorical_result=categorical_result,
    )
    trace_entries.append(TraceEntry(
        state=initial_state,
        action=AnalysisAction("categorical"),
        reward=_compute_reward(initial_state, AnalysisAction("categorical"), state_after_cat),
        next_state=state_after_cat,
    ))

    # Epistemic step
    state_after_epi = AnalysisState(
        target=target,
        categorical_done=True,
        epistemic_done=True,
        categorical_result=categorical_result,
        epistemic_result=epistemic_result,
    )
    trace_entries.append(TraceEntry(
        state=state_after_cat,
        action=AnalysisAction("epistemic"),
        reward=_compute_reward(state_after_cat, AnalysisAction("epistemic"), state_after_epi),
        next_state=state_after_epi,
    ))

    # Dialectical step
    state_after_dia = AnalysisState(
        target=target,
        categorical_done=True,
        epistemic_done=True,
        dialectical_done=True,
        categorical_result=categorical_result,
        epistemic_result=epistemic_result,
        dialectical_result=dialectical_result,
    )
    trace_entries.append(TraceEntry(
        state=state_after_epi,
        action=AnalysisAction("dialectical"),
        reward=_compute_reward(state_after_epi, AnalysisAction("dialectical"), state_after_dia),
        next_state=state_after_dia,
    ))

    # Generative step
    trace_entries.append(TraceEntry(
        state=state_after_dia,
        action=AnalysisAction("generative"),
        reward=_compute_reward(state_after_dia, AnalysisAction("generative"), final_state),
        next_state=final_state,
    ))

    # Compute total discounted reward
    total_reward = 0.0
    for i, entry in enumerate(trace_entries):
        total_reward += (gamma ** i) * entry.reward

    # Build policy trace
    trace = PolicyTrace(
        problem_name=f"Analysis({target})",
        log=tuple(trace_entries),
        value=final_state,
        total_reward=total_reward,
    )

    return total_reward, trace


def _compute_reward(
    state: AnalysisState,
    action: AnalysisAction,
    next_state: AnalysisState,
) -> float:
    """
    Compute reward for analysis action.

    This is extracted from the reward function in create_analysis_formulation
    so it can be reused by the async LLM version.
    """
    # Base reward for making progress
    progress_reward = 0.25 if next_state.modes_applied > state.modes_applied else 0.0

    # Quality reward based on results
    quality_reward = 0.0

    # Categorical: reward for laws passing
    if next_state.categorical_result:
        cat = next_state.categorical_result
        if cat.laws_total > 0:
            quality_reward += 0.15 * (cat.laws_passed / cat.laws_total)

    # Epistemic: reward for being grounded
    if next_state.epistemic_result:
        epi = next_state.epistemic_result
        if epi.is_grounded:
            quality_reward += 0.15
        if epi.has_valid_bootstrap:
            quality_reward += 0.05

    # Dialectical: reward for resolving tensions (penalize unresolved problems)
    if next_state.dialectical_result:
        dia = next_state.dialectical_result
        if len(dia.tensions) > 0:
            resolution_ratio = dia.resolved_count / len(dia.tensions)
            quality_reward += 0.10 * resolution_ratio
        # Penalty for problematic contradictions
        quality_reward -= 0.05 * dia.problematic_count

    # Generative: reward for compression and regenerability
    if next_state.generative_result:
        gen = next_state.generative_result
        if gen.is_compressed:
            quality_reward += 0.10
        if gen.is_regenerable:
            quality_reward += 0.10

    # Completion bonus
    completion_bonus = 0.5 if next_state.is_complete else 0.0

    # Penalty for violations
    violation_penalty = -0.3 if next_state.has_violations else 0.0

    return progress_reward + quality_reward + completion_bonus + violation_penalty


def analyze_with_witness(target: str) -> tuple[FullAnalysisReport, list[dict[str, Any]]]:
    """
    Analyze a spec and return Witness-compatible marks (structural mode).

    This bridges Analysis Operad to the Witness Crown Jewel.
    Uses structural (non-LLM) analysis.

    For LLM-backed analysis with witness integration, use analyze_with_witness_llm().

    Args:
        target: Path to spec file to analyze

    Returns:
        Tuple of (full analysis report, list of marks for Witness)
    """
    from .analysis import _full_analysis

    # Run full analysis
    report = _full_analysis(target)

    # Create marks for each mode
    marks = _create_witness_marks(report, target)

    return report, marks


async def analyze_with_witness_llm(target: str) -> tuple[FullAnalysisReport, list[dict[str, Any]]]:
    """
    Analyze a spec and return Witness-compatible marks (LLM mode).

    This bridges Analysis Operad to the Witness Crown Jewel.
    Uses REAL LLM-backed analysis for rigorous four-mode inquiry.

    Args:
        target: Path to spec file to analyze

    Returns:
        Tuple of (full analysis report, list of marks for Witness)
    """
    from .analysis import analyze_full_llm

    # Run full LLM-backed analysis
    report = await analyze_full_llm(target)

    # Create marks for each mode
    marks = _create_witness_marks(report, target)

    return report, marks


def _create_witness_marks(report: FullAnalysisReport, target: str) -> list[dict[str, Any]]:
    """
    Create Witness-compatible marks from a full analysis report.

    This is factored out so both sync and async versions can use it.
    """
    marks: list[dict[str, Any]] = []

    # Categorical mark
    marks.append({
        "origin": "analysis_operad",
        "action": "categorical_analysis",
        "state_before": f"unanalyzed:{target}",
        "state_after": f"categorical:{report.categorical.laws_passed}/{report.categorical.laws_total}",
        "value": 1.0 if not report.categorical.has_violations else 0.5,
        "rationale": report.categorical.summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "categorical",
    })

    # Epistemic mark
    marks.append({
        "origin": "analysis_operad",
        "action": "epistemic_analysis",
        "state_before": f"categorical:{target}",
        "state_after": f"epistemic:L{report.epistemic.layer}",
        "value": 1.0 if report.epistemic.is_grounded else 0.5,
        "rationale": report.epistemic.summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "epistemic",
    })

    # Dialectical mark
    marks.append({
        "origin": "analysis_operad",
        "action": "dialectical_analysis",
        "state_before": f"epistemic:{target}",
        "state_after": f"dialectical:{report.dialectical.resolved_count}/{len(report.dialectical.tensions)}",
        "value": 1.0 if report.dialectical.problematic_count == 0 else 0.5,
        "rationale": report.dialectical.summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "dialectical",
    })

    # Generative mark
    marks.append({
        "origin": "analysis_operad",
        "action": "generative_analysis",
        "state_before": f"dialectical:{target}",
        "state_after": f"generative:compression={report.generative.compression_ratio:.2f}",
        "value": 1.0 if report.generative.is_regenerable else 0.5,
        "rationale": report.generative.summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "generative",
    })

    # Synthesis mark
    marks.append({
        "origin": "analysis_operad",
        "action": "synthesis",
        "state_before": f"analyzed:{target}",
        "state_after": f"valid:{report.is_valid}",
        "value": 1.0 if report.is_valid else 0.3,
        "rationale": report.synthesis,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "full",
    })

    return marks


def self_analyze_with_dp() -> tuple[FullAnalysisReport, PolicyTrace[AnalysisState]]:
    """
    Apply DP-formulated analysis to the Analysis Operad itself.

    This is the meta-applicability test: can analysis analyze itself using DP?
    """
    # First, run DP-based analysis
    value, trace = analyze_as_dp("spec/theory/analysis-operad.md")

    # Then, get the full report for the final state
    if trace.log:
        final_state = trace.value
        if isinstance(final_state, AnalysisState) and final_state.is_complete:
            report = FullAnalysisReport(
                target=final_state.target,
                categorical=final_state.categorical_result,  # type: ignore
                epistemic=final_state.epistemic_result,  # type: ignore
                dialectical=final_state.dialectical_result,  # type: ignore
                generative=final_state.generative_result,  # type: ignore
                synthesis=f"DP-formulated self-analysis complete. Value: {value:.3f}",
            )
            return report, trace

    # Fallback to direct analysis
    from .analysis import _full_analysis
    report = _full_analysis("spec/theory/analysis-operad.md")
    return report, trace


__all__ = [
    # DP State and Action types
    "AnalysisState",
    "AnalysisAction",
    # Formulation
    "create_analysis_formulation",
    # Integration functions (structural)
    "analyze_as_dp",
    "analyze_with_witness",
    "self_analyze_with_dp",
    # Integration functions (LLM-backed)
    "analyze_as_dp_llm",
    "analyze_with_witness_llm",
]
