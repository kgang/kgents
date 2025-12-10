"""
Psi-gent MetaphorEvolutionAgent: E-gent integration for dialectical metaphor learning.

Applies E-gent's evolution pipeline to metaphors:
- Thesis: Current best metaphor for problem type
- Antithesis: Failed alternative or shadow metaphor
- Synthesis: Evolved metaphor that transcends both

Enables: Metaphor improvement through experimental methodology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from .types import (
    Metaphor,
    Novel,
)
from .holographic_library import HolographicMetaphorLibrary
from .metaphor_historian import MetaphorHistorian


# =============================================================================
# Evolution Types
# =============================================================================


class Verdict(Enum):
    """Judge verdict on an evolution experiment."""

    ACCEPT = "accept"  # Synthesis is better
    REVISE = "revise"  # Need more work
    REJECT = "reject"  # Antithesis fails
    HOLD = "hold"  # Tension cannot be resolved


@dataclass(frozen=True)
class MetaphorHypothesis:
    """A hypothesis for metaphor improvement."""

    hypothesis_id: str
    thesis: Metaphor
    antithesis: Metaphor
    rationale: str
    improvement_type: str  # "operations", "scope", "blend"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ExperimentResult:
    """Result of testing a metaphor hypothesis."""

    hypothesis: MetaphorHypothesis
    test_problems: tuple[Novel, ...]
    success_count: int
    total_count: int
    avg_distortion: float
    notes: str

    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


@dataclass(frozen=True)
class HeldTension:
    """A tension that cannot be resolved dialectically."""

    thesis: Metaphor
    antithesis: Metaphor
    reason: str
    recommended_action: str


@dataclass(frozen=True)
class MetaphorEvolutionResult:
    """Output from the metaphor evolution process."""

    evolved_metaphor: Metaphor | None
    held_tensions: tuple[HeldTension, ...]
    experiments_run: int
    accepted_count: int
    verdict: Verdict


# =============================================================================
# Shadow Metaphor Surfacing
# =============================================================================


@dataclass(frozen=True)
class CollectiveShadow:
    """The metaphors in the system's collective shadow."""

    unused_domains: tuple[str, ...]
    always_rejected: tuple[Metaphor, ...]
    unexplored_blends: tuple[tuple[str, str], ...]  # Pairs of metaphor IDs
    shadow_analysis: str


@dataclass
class MetaphorShadowAnalyzer:
    """
    Surfaces the metaphors the system avoids.

    Like Jung's collective shadow - content exiled to maintain identity.
    For Ψ-gent: metaphor families never tried, always avoided.
    """

    def analyze(self, library: HolographicMetaphorLibrary) -> CollectiveShadow:
        """Analyze the library's shadow metaphors."""
        stats = library.get_usage_statistics()

        # Find unused domains
        unused_domains = self._find_unused_domains(stats)

        # Find always-rejected metaphors (never successful)
        always_rejected = self._find_always_rejected(library, stats)

        # Find unexplored blends
        unexplored_blends = self._find_unexplored_blends(library)

        # Build analysis narrative
        analysis = self._build_shadow_analysis(
            unused_domains, always_rejected, unexplored_blends
        )

        return CollectiveShadow(
            unused_domains=tuple(unused_domains),
            always_rejected=tuple(always_rejected),
            unexplored_blends=tuple(unexplored_blends),
            shadow_analysis=analysis,
        )

    def _find_unused_domains(self, stats: dict[str, dict[str, Any]]) -> list[str]:
        """Find domains with no successful usage."""
        # Collect all domains
        domain_usage: dict[str, int] = {}
        for mid, s in stats.items():
            # Extract domain from metaphor (simplified)
            parts = mid.split("_")
            domain = parts[0] if parts else "unknown"
            usage = s.get("usage_count", 0)
            domain_usage[domain] = domain_usage.get(domain, 0) + usage

        # Return domains with zero usage
        return [d for d, u in domain_usage.items() if u == 0]

    def _find_always_rejected(
        self, library: HolographicMetaphorLibrary, stats: dict[str, dict[str, Any]]
    ) -> list[Metaphor]:
        """Find metaphors with zero success rate despite attempts."""
        rejected = []
        for mid, s in stats.items():
            usage = s.get("usage_count", 0)
            success_rate = s.get("success_rate", 0.5)
            if usage > 2 and success_rate == 0:
                metaphor = library.get(mid)
                if metaphor:
                    rejected.append(metaphor)
        return rejected

    def _find_unexplored_blends(
        self, library: HolographicMetaphorLibrary
    ) -> list[tuple[str, str]]:
        """Find metaphor pairs that have never been blended."""
        all_metaphors = library.all_metaphors()
        existing_blends = set()

        # Find existing blends
        for m in all_metaphors:
            if m.metaphor_id.startswith("blend_"):
                # Extract constituent IDs
                for related in m.related_metaphors:
                    existing_blends.add(related)

        # Find pairs not yet blended (limit to avoid combinatorial explosion)
        unexplored = []
        non_blends = [
            m for m in all_metaphors if not m.metaphor_id.startswith("blend_")
        ]

        for i, m1 in enumerate(non_blends[:5]):
            for m2 in non_blends[i + 1 : 6]:
                pair = (m1.metaphor_id, m2.metaphor_id)
                if (
                    m1.metaphor_id not in existing_blends
                    or m2.metaphor_id not in existing_blends
                ):
                    unexplored.append(pair)

        return unexplored[:5]  # Limit results

    def _build_shadow_analysis(
        self,
        unused_domains: list[str],
        always_rejected: list[Metaphor],
        unexplored_blends: list[tuple[str, str]],
    ) -> str:
        """Build a narrative analysis of the shadow."""
        lines = [
            "=== Metaphor Shadow Analysis ===",
            "",
        ]

        if unused_domains:
            lines.append(f"Unused domains: {', '.join(unused_domains)}")
            lines.append("  → These domains may contain valuable metaphors")
            lines.append("")

        if always_rejected:
            names = [m.name for m in always_rejected]
            lines.append(f"Always rejected: {', '.join(names)}")
            lines.append("  → May indicate bias or missed opportunities")
            lines.append("")

        if unexplored_blends:
            blend_names = [f"{a[:8]}×{b[:8]}" for a, b in unexplored_blends]
            lines.append(f"Unexplored blends: {', '.join(blend_names)}")
            lines.append("  → Novel combinations may yield breakthrough metaphors")

        return "\n".join(lines)


# =============================================================================
# Metaphor Evolution Agent
# =============================================================================


@dataclass
class MetaphorEvolutionAgent:
    """
    Evolve metaphors through dialectical process.

    E-gent integration for Ψ-gent:
    - Ground: Analyze current metaphor performance
    - Hypothesis: Generate improvement proposals from shadow
    - Experiment: Test each hypothesis on sample problems
    - Judge: Evaluate against principles
    - Sublate: Synthesize or hold tension
    """

    library: HolographicMetaphorLibrary = field(
        default_factory=HolographicMetaphorLibrary
    )
    historian: MetaphorHistorian = field(default_factory=MetaphorHistorian)
    shadow_analyzer: MetaphorShadowAnalyzer = field(
        default_factory=MetaphorShadowAnalyzer
    )

    # Configuration
    acceptance_threshold: float = 0.6  # Success rate to accept
    distortion_threshold: float = 0.5  # Max acceptable distortion

    def evolve(
        self,
        current_metaphor: Metaphor,
        test_problems: list[Novel],
        shadow_metaphors: list[Metaphor] | None = None,
    ) -> MetaphorEvolutionResult:
        """
        Run the full evolution pipeline.

        Returns evolved metaphor or held tensions.
        """
        # Stage 1: Ground - Analyze current performance
        performance = self._analyze_performance(current_metaphor, test_problems)

        # Stage 2: Hypothesis - Generate improvement proposals
        if shadow_metaphors is None:
            shadow = self.shadow_analyzer.analyze(self.library)
            shadow_metaphors = list(shadow.always_rejected)

        hypotheses = self._generate_hypotheses(
            current_metaphor, performance, shadow_metaphors
        )

        # Stage 3: Experiment - Test each hypothesis
        experiments = []
        for hypothesis in hypotheses:
            result = self._run_experiment(hypothesis, test_problems)
            experiments.append(result)

        # Stage 4: Judge - Evaluate against principles
        verdicts = [(e, self._judge(e)) for e in experiments]

        # Stage 5: Sublate - Synthesize or hold tension
        accepted = [e for e, v in verdicts if v == Verdict.ACCEPT]

        if accepted:
            best = max(accepted, key=lambda e: e.success_rate)
            synthesis = self._sublate(current_metaphor, best.hypothesis.antithesis)
            return MetaphorEvolutionResult(
                evolved_metaphor=synthesis,
                held_tensions=(),
                experiments_run=len(experiments),
                accepted_count=len(accepted),
                verdict=Verdict.ACCEPT,
            )
        else:
            # Hold tensions for unresolved cases
            tensions = self._extract_tensions(experiments)
            return MetaphorEvolutionResult(
                evolved_metaphor=None,
                held_tensions=tuple(tensions),
                experiments_run=len(experiments),
                accepted_count=0,
                verdict=Verdict.HOLD,
            )

    def _analyze_performance(
        self, metaphor: Metaphor, problems: list[Novel]
    ) -> dict[str, Any]:
        """Stage 1: Ground - Analyze current metaphor performance."""
        stats = self.library.get_usage_statistics()
        metaphor_stats = stats.get(metaphor.metaphor_id, {})

        return {
            "metaphor_id": metaphor.metaphor_id,
            "usage_count": metaphor_stats.get("usage_count", 0),
            "success_rate": metaphor_stats.get("success_rate", 0.5),
            "resolution": metaphor_stats.get("resolution", 1.0),
            "is_hot": metaphor_stats.get("is_hot", False),
            "is_cold": metaphor_stats.get("is_cold", False),
            "test_problem_count": len(problems),
        }

    def _generate_hypotheses(
        self,
        thesis: Metaphor,
        performance: dict[str, Any],
        shadow_metaphors: list[Metaphor],
    ) -> list[MetaphorHypothesis]:
        """Stage 2: Hypothesis - Generate improvement proposals."""
        hypotheses = []

        # Hypothesis type 1: Blend with high-performing metaphor
        all_metaphors = self.library.all_metaphors()
        hot_metaphors = [
            m
            for m in all_metaphors
            if self.library.get_usage_statistics()
            .get(m.metaphor_id, {})
            .get("is_hot", False)
        ]

        for hot in hot_metaphors[:2]:
            if hot.metaphor_id != thesis.metaphor_id:
                hypotheses.append(
                    MetaphorHypothesis(
                        hypothesis_id=str(uuid4()),
                        thesis=thesis,
                        antithesis=hot,
                        rationale=f"Blend with high-performing {hot.name}",
                        improvement_type="blend",
                    )
                )

        # Hypothesis type 2: Shadow integration
        for shadow in shadow_metaphors[:2]:
            hypotheses.append(
                MetaphorHypothesis(
                    hypothesis_id=str(uuid4()),
                    thesis=thesis,
                    antithesis=shadow,
                    rationale=f"Integrate shadow metaphor {shadow.name}",
                    improvement_type="shadow",
                )
            )

        # Hypothesis type 3: Operation expansion
        # Find metaphors with more operations
        richer = [
            m
            for m in all_metaphors
            if len(m.operations) > len(thesis.operations) and m.domain == thesis.domain
        ]
        for rich in richer[:1]:
            hypotheses.append(
                MetaphorHypothesis(
                    hypothesis_id=str(uuid4()),
                    thesis=thesis,
                    antithesis=rich,
                    rationale=f"Expand operations from {rich.name}",
                    improvement_type="operations",
                )
            )

        return hypotheses

    def _run_experiment(
        self, hypothesis: MetaphorHypothesis, problems: list[Novel]
    ) -> ExperimentResult:
        """Stage 3: Experiment - Test the hypothesis."""
        # Create synthesized metaphor for testing
        synthesized = self._create_synthesis(hypothesis.thesis, hypothesis.antithesis)

        # Test on problems (simplified - just check tractability match)
        success_count = 0
        total_distortion = 0.0

        for problem in problems:
            # Simplified test: does synthesized metaphor match problem complexity?
            complexity_match = abs(synthesized.tractability - problem.complexity) < 0.4
            domain_match = (
                synthesized.domain == problem.domain or synthesized.generality > 0.6
            )

            if complexity_match and domain_match:
                success_count += 1
                total_distortion += 0.2  # Low distortion on success
            else:
                total_distortion += 0.6  # Higher distortion on failure

        avg_distortion = total_distortion / len(problems) if problems else 1.0

        return ExperimentResult(
            hypothesis=hypothesis,
            test_problems=tuple(problems),
            success_count=success_count,
            total_count=len(problems),
            avg_distortion=avg_distortion,
            notes=f"Tested {len(problems)} problems",
        )

    def _create_synthesis(self, thesis: Metaphor, antithesis: Metaphor) -> Metaphor:
        """Create a preliminary synthesis for testing."""
        # Combine operations
        combined_ops = list(thesis.operations)
        for op in antithesis.operations:
            if op.name not in [o.name for o in combined_ops]:
                combined_ops.append(op)

        return Metaphor(
            metaphor_id=f"synth_{thesis.metaphor_id[:8]}_{antithesis.metaphor_id[:8]}",
            name=f"Synthesis({thesis.name}, {antithesis.name})",
            domain=thesis.domain,  # Primary domain from thesis
            description=f"Synthesis of {thesis.name} and {antithesis.name}",
            operations=tuple(combined_ops[:10]),  # Limit operations
            tractability=(thesis.tractability + antithesis.tractability) / 2,
            generality=max(thesis.generality, antithesis.generality),
            related_metaphors=(thesis.metaphor_id, antithesis.metaphor_id),
        )

    def _judge(self, experiment: ExperimentResult) -> Verdict:
        """Stage 4: Judge - Evaluate against principles."""
        # Accept if success rate and distortion are acceptable
        if (
            experiment.success_rate >= self.acceptance_threshold
            and experiment.avg_distortion <= self.distortion_threshold
        ):
            return Verdict.ACCEPT

        # Revise if close to threshold
        if (
            experiment.success_rate >= self.acceptance_threshold * 0.8
            and experiment.avg_distortion <= self.distortion_threshold * 1.2
        ):
            return Verdict.REVISE

        # Hold if there's potential but needs human judgment
        if experiment.success_rate > 0.3:
            return Verdict.HOLD

        # Reject otherwise
        return Verdict.REJECT

    def _sublate(self, thesis: Metaphor, antithesis: Metaphor) -> Metaphor:
        """Stage 5: Sublate - Create final synthesis that transcends both."""
        # Use holographic blending
        blended = self.library.blend([thesis, antithesis])
        if blended:
            # Register the evolved metaphor
            self.library.register(blended)

            # Record in historian
            ctx = self.historian.begin_trace(
                action="EVOLVE",
                input_obj={
                    "thesis": thesis.metaphor_id,
                    "antithesis": antithesis.metaphor_id,
                },
            )
            self.historian.end_trace(
                ctx,
                outputs={
                    "evolved_id": blended.metaphor_id,
                    "thesis": thesis.name,
                    "antithesis": antithesis.name,
                },
            )

            return blended

        # Fallback to simple synthesis
        return self._create_synthesis(thesis, antithesis)

    def _extract_tensions(
        self, experiments: list[ExperimentResult]
    ) -> list[HeldTension]:
        """Extract held tensions from failed experiments."""
        tensions = []
        for e in experiments:
            verdict = self._judge(e)
            if verdict in (Verdict.HOLD, Verdict.REJECT):
                tensions.append(
                    HeldTension(
                        thesis=e.hypothesis.thesis,
                        antithesis=e.hypothesis.antithesis,
                        reason=f"Success rate {e.success_rate:.1%}, distortion {e.avg_distortion:.2f}",
                        recommended_action=(
                            "Human review needed"
                            if verdict == Verdict.HOLD
                            else "Consider alternative antithesis"
                        ),
                    )
                )
        return tensions


# =============================================================================
# Evolution Learning (Institutional Memory)
# =============================================================================


@dataclass
class EvolutionMemory:
    """
    Institutional memory for metaphor evolution.

    Tracks what worked, what failed, and why.
    """

    successful_evolutions: list[MetaphorEvolutionResult] = field(default_factory=list)
    failed_evolutions: list[MetaphorEvolutionResult] = field(default_factory=list)
    held_tensions_history: list[HeldTension] = field(default_factory=list)

    def record(self, result: MetaphorEvolutionResult) -> None:
        """Record an evolution result."""
        if result.evolved_metaphor:
            self.successful_evolutions.append(result)
        else:
            self.failed_evolutions.append(result)

        for tension in result.held_tensions:
            self.held_tensions_history.append(tension)

    def get_success_patterns(self) -> list[str]:
        """Identify patterns in successful evolutions."""
        patterns = []
        for result in self.successful_evolutions:
            if result.evolved_metaphor:
                if result.evolved_metaphor.metaphor_id.startswith("blend_"):
                    patterns.append("blend")
                elif "shadow" in result.evolved_metaphor.description.lower():
                    patterns.append("shadow_integration")
                else:
                    patterns.append("synthesis")
        return patterns

    def should_avoid(self, hypothesis: MetaphorHypothesis) -> bool:
        """Check if this hypothesis type has repeatedly failed."""
        similar_failures = 0
        for result in self.failed_evolutions:
            for tension in result.held_tensions:
                if (
                    tension.thesis.domain == hypothesis.thesis.domain
                    and tension.antithesis.domain == hypothesis.antithesis.domain
                ):
                    similar_failures += 1

        return similar_failures >= 3  # Avoid after 3 similar failures
